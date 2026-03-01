# GovScape base image for both API and embedding servers, and the dev container.

# The GitHub action has a build matrix that specifies the versions.
# These ARGs are the fallback.
ARG PYTHON_VERSION=3.11.14-trixie

# We use a separate build phase to reduce the size of the final image.
FROM python:${PYTHON_VERSION} AS builder

ARG LUCENE_VERSION=10.0.0
ARG LUCENE_SHA256="100c3d61d6799ac16b7b8c1826cddf07fb1715141ebdb0d7b8119cdd96b24574  pylucene-10.0.0-src.tar.gz"

ENV DEBIAN_FRONTEND=noninteractive

# Dependencies for the pylucene build.
RUN pip install --upgrade pip setuptools wheel build \
    && apt-get update \
    && apt-get install -y \
        build-essential \
        default-jdk \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/lib/jvm/default-java /usr/lib/jvm/temurin

# Download pylucene, verify, build, and install.
WORKDIR /usr/src/pylucene
RUN curl -fsSL https://downloads.apache.org/lucene/pylucene/pylucene-${LUCENE_VERSION}-src.tar.gz -o pylucene-${LUCENE_VERSION}-src.tar.gz \
    && echo "${LUCENE_SHA256}" | sha256sum -c - \
    && tar -xz --strip-components=1 -f pylucene-${LUCENE_VERSION}-src.tar.gz \
    && cd jcc \
    && NO_SHARED=1 JCC_JDK=/usr/lib/jvm/temurin python -m build -nw \
    && pip install dist/*.whl \
    && cd .. \
    && make all install JCC='python -m jcc' PYTHON=python NUM_FILES=16 MODERN_PACKAGING=true

# New stage for runtime. Only preserve necessary files.
# Python, and pylucene remain after copying.
FROM python:${PYTHON_VERSION} AS runtime

ARG POETRY_VERSION=2.3.2

# We will allow poetry to access system site packages, which allows us to use the globally installed pylucene package.
# We will also need to configure poetry to not use in-project venvs, since any out-of-container venvs won't have lucene and won't be recreated.
ENV POETRY_VIRTUALENVS_OPTIONS_SYSTEM_SITE_PACKAGES=true
ENV POETRY_VIRTUALENVS_IN_PROJECT=false

ENV POETRY_HOME=/opt/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/lib/jvm/default-java /usr/lib/jvm/temurin \
    && python3 -m venv ${POETRY_HOME} \
    && ${POETRY_HOME}/bin/pip install poetry==${POETRY_VERSION}

COPY --from=builder /usr/local /usr/local
