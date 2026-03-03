<template>
  <div class="public-layout">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="container nav-inner">
        <router-link to="/" class="nav-brand">
          <span class="brand-icon">🍽</span>
          <span>Mesa<strong>Reserva</strong></span>
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Reservar</router-link>
          <router-link to="/cancel" class="nav-link">Cancelar</router-link>
        </div>
      </div>
    </nav>
    <main>
      <slot />
    </main>
    <footer class="footer">
      <p>© 2026 MesaReserva. Todos los derechos reservados.</p>
    </footer>
  </div>
</template>

<style scoped>
.public-layout { display: flex; flex-direction: column; min-height: 100vh; }
.navbar {
  background: rgba(15,13,10,0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-inner { display: flex; align-items: center; justify-content: space-between; height: 64px; }
.nav-brand { display: flex; align-items: center; gap: 0.5rem; font-size: 1.2rem; color: var(--text); }
.brand-icon { font-size: 1.4rem; }
.nav-brand strong { color: var(--primary); }
.nav-links { display: flex; gap: 1.5rem; }
.nav-link { color: var(--text-muted); font-size: 0.9rem; font-weight: 500; transition: color 0.2s; }
.nav-link:hover, .nav-link.router-link-active { color: var(--primary); }
main { flex: 1; }
.footer { border-top: 1px solid var(--border); padding: 1.5rem; text-align: center; }
.footer p { font-size: 0.85rem; }
</style>
