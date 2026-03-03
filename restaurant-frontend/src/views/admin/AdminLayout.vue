<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">
        <span>🍽</span> Admin
      </div>
      <nav class="sidebar-nav">
        <router-link to="/admin" exact-active-class="active" class="sidebar-link">📅 Dashboard</router-link>
        <router-link to="/admin/tables" active-class="active" class="sidebar-link">🪑 Mesas</router-link>
        <router-link to="/admin/schedule" active-class="active" class="sidebar-link">⏰ Horarios</router-link>
        <hr class="divider" />
        <router-link to="/" class="sidebar-link">🌐 Ver sitio</router-link>
        <button class="sidebar-link sidebar-logout" @click="logout">🚪 Salir</button>
      </nav>
    </aside>
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

function logout() {
  authStore.logout()
  router.push({ name: 'admin-login' })
}
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }
.sidebar {
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  width: 220px;
  flex-shrink: 0;
}
.sidebar-brand { color: var(--primary); font-size: 1.2rem; font-weight: 800; padding: 0 1.5rem 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 1rem; }
.sidebar-nav { display: flex; flex-direction: column; gap: 0.25rem; padding: 0 0.75rem; }
.sidebar-link {
  align-items: center;
  background: none;
  border: none;
  border-radius: 8px;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0.6rem 0.75rem;
  text-align: left;
  transition: all 0.2s;
  width: 100%;
  gap: 0.5rem;
}
.sidebar-link:hover, .sidebar-link.active { background: rgba(212,168,67,0.1); color: var(--primary); }
.sidebar-logout { color: var(--error); }
.sidebar-logout:hover { background: rgba(248,113,113,0.1); color: var(--error); }
.admin-main { flex: 1; padding: 2rem; overflow: auto; }
@media (max-width: 768px) {
  .admin-layout { flex-direction: column; }
  .sidebar { width: 100%; min-height: auto; position: relative; }
}
</style>
