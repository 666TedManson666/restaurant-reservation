<template>
  <div class="page-center">
    <div class="card login-card">
      <div class="gold-line"></div>
      <h2>Panel Admin</h2>
      <p>Ingresa con tus credenciales de administrador.</p>
      <hr class="divider" />

      <transition name="fade">
        <div v-if="error" class="alert alert-error">{{ error }}</div>
      </transition>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Usuario</label>
          <input v-model="form.username" class="form-control" type="text" placeholder="admin" required :disabled="loading" />
        </div>
        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <input v-model="form.password" class="form-control" type="password" placeholder="••••••••" required :disabled="loading" />
        </div>
        <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Ingresando...' : 'Iniciar Sesión' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    router.push({ name: 'admin-dashboard' })
  } catch {
    error.value = 'Credenciales incorrectas. Intenta de nuevo.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card { max-width: 400px; width: 100%; }
</style>
