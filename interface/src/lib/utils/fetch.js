const IS_DEV = import.meta.env.DEV;

// Default API request timeout (10 seconds)
const DEFAULT_API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS || 10000);

const ENDPOINTS = {
  DEV: {
    API: 'http://localhost:8080/api',
    S3: 'https://bcgl-public-bucket.s3.amazonaws.com/dev-serving/img'
  },
  PROD: {
    API: 'https://govscape.net/api',
    S3: 'https://bcgl-public-bucket.s3.amazonaws.com/prod-serving/img'
  }
};

export const getApiBaseUrl = () => {
  if (IS_DEV) return ENDPOINTS.DEV.API;

  return ENDPOINTS.PROD.API;
};

export const getImageBaseUrl = () => {
  if (IS_DEV) return ENDPOINTS.DEV.S3;

  return ENDPOINTS.PROD.S3;
};

export async function apiFetch(endpoint, options = {}) {
    const defaultOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include',
    };

    const {
        timeoutMs = DEFAULT_API_TIMEOUT_MS,
        signal: externalSignal,
        ...restOptions
    } = options || {};

    const mergedOptions = {
        ...defaultOptions,
        ...restOptions,
        headers: {
            ...defaultOptions.headers,
            ...restOptions.headers,
        },
    };

    try {
        const apiUrl = getApiBaseUrl();
        const controller = !externalSignal ? new AbortController() : null;
        const timeoutId = !externalSignal
            ? setTimeout(() => controller.abort(), Math.max(0, timeoutMs))
            : null;

        const response = await fetch(`${apiUrl}${endpoint}`, {
            ...mergedOptions,
            signal: externalSignal || (controller && controller.signal) || undefined,
        });

        if (timeoutId) clearTimeout(timeoutId);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error?.name === 'AbortError') {
            throw new Error('Request timed out');
        }
        console.error('API request failed:', error);
        throw error;
    }
}
