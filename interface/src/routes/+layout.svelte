<script>
  import { page } from '$app/stores';
</script>

<div class="app">
  <header>
    <a href="/" class="logo">
      <img draggable="false" src="/logo.png" alt="GovScape Logo" class="logo-image" />
    </a>
  </header>
  {#key $page.url.pathname}
    <slot />
  {/key}
</div>

<style>
  header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: #fff;
    border-bottom: 1px solid #e9ecef;
    height: var(--header-height);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
  }

  .logo img {
    height: 40px;
    width: auto;
    vertical-align: middle;
  }

  nav {
    display: flex;
    gap: 2rem;
  }

  nav a {
    color: var(--text-color-primary);
    font-size: 0.85rem;
    text-decoration: none;
  }

  footer {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50px;
    background-color: var(--color-secondary);
    color: #fff;
  }

  .footer-content {
    text-align: center;
    font-family: var(--serif-font);
    font-size: 0.8rem;
  }
</style>
