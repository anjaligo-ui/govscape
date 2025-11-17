<script>
  import { onMount, onDestroy } from 'svelte';
  import { searchStore, searchActions } from '$lib/stores/search';
  import SearchBox from '$lib/components/SearchBox.svelte';
  import TypingEffect from '$lib/components/TypingEffect.svelte';

  const govDomains = [
    'epa.gov',
    'nsa.gov',
    'usda.gov',
    'sec.gov',
    'gpo.gov',
    'archives.gov',
  ];

  let isSmallScreen = false;

  function checkScreenSize() {
    isSmallScreen = window.innerWidth < 768;
  }

  onMount(() => {
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
  });

  onDestroy(() => {
    window.removeEventListener('resize', checkScreenSize);
    searchActions.reset();
  });
</script>

<svelte:head>
  <title>GovScape - Search 10+ Million Government PDFs</title>
</svelte:head>

<main>
  <div class="title-container">
    <h1>
      {#if isSmallScreen}
        Search 10+ Million PDFs across<br /><TypingEffect words={govDomains} />
      {:else}
        Search 10+ Million PDFs across <TypingEffect words={govDomains} />
      {/if}
    </h1>
  </div>
  <SearchBox />

  <div class="resources-section">
    <a href="https://arxiv.org/abs/2511.11010" target="_blank" rel="noopener noreferrer" class="resource-card">
      <div class="card-image">
        <iframe
          src="https://arxiv.org/pdf/2511.11010"
          title="GovScape: A Public Multimodal Search System for 70 Million Pages of Government PDFs"
          frameborder="0"
          class="arxiv-iframe"
        ></iframe>
      </div>
      <div class="card-content">
        <h3 class="card-title">
          arXiv Paper
        </h3>
      </div>
    </a>

    <a href="https://youtu.be/mNda8lVKT1U" target="_blank" rel="noopener noreferrer" class="resource-card">
      <div class="card-image">
        <iframe
          src="https://www.youtube.com/embed/mNda8lVKT1U?autoplay=1&mute=1&loop=1&playlist=mNda8lVKT1U&controls=0&modestbranding=1&rel=0"
          title="GovScape: A Tutorial Video"
          frameborder="0"
          allow="autoplay; encrypted-media"
          allowfullscreen
          class="video-iframe"
        ></iframe>
      </div>
      <div class="card-content">
        <h3 class="card-title">
          Demo Video
        </h3>
      </div>
    </a>
  </div>
</main>

<style>
  main {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: calc(100vh - 50px);
    padding-top: 15vh;
  }

  .title-container {
    width: 98vw;
    max-width: 100vw;
    text-align: center;
  }

  .title-container h1 {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1.35;
    padding: 2rem;
    margin-bottom: 1.5rem;
  }

  .resources-section {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
    width: 40vw;
    min-width: 500px;
    margin-top: 6rem;
    margin-bottom: 3rem;
  }

  .resource-card {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
    overflow: hidden;
    text-decoration: none;
    color: var(--text-color-primary);
    transition: transform 0.2s, box-shadow 0.2s;
    display: flex;
    flex-direction: column;
  }

  .resource-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 12px rgba(0, 110, 185, 0.15);
  }

  .card-image {
    position: relative;
    width: 100%;
    height: 140px;
    overflow: hidden;
  }

  .arxiv-preview,
  .video-preview {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: var(--color-primary);
  }

  .arxiv-preview {
    background: linear-gradient(135deg, var(--background-color-primary) 0%, #c8dff5 100%);
  }

  .video-preview {
    background: linear-gradient(135deg, #ffe8e8 0%, #ffd1d1 100%);
    color: #c41e3a;
  }

  .arxiv-preview i,
  .video-preview i {
    font-size: 2.5rem;
    opacity: 0.9;
  }

  .arxiv-iframe,
  .video-iframe {
    width: 100%;
    height: 100%;
    border: none;
    pointer-events: none;
  }

  .card-content {
    padding: 0.85rem 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-title {
    font-family: var(--sans-serif-font);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-primary);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.4rem;
  }

  .card-title i {
    font-size: 1rem;
  }

  @media (max-width: 767px) {
    main {
      padding-top: 50px;
    }

    .resources-section {
      grid-template-columns: 1fr;
      width: 75vw;
      min-width: unset;
      gap: 1rem;
      margin-top: 3rem;
    }

    .card-image {
      height: 100px;
    }

    .arxiv-preview i,
    .video-preview i {
      font-size: 2rem;
    }
  }
</style>
