<template>
  <PublicLayout>
    <div class="page-center">
      <div class="card" style="max-width:480px; width:100%">
        <h2>Cancelar Reserva</h2>
        <p>Ingresa tu código de cancelación para cancelar tu reserva.</p>
        <hr class="divider" />

        <transition name="fade">
          <div v-if="success" class="alert alert-success">
            ✓ Reserva cancelada exitosamente. La mesa ha sido liberada.
          </div>
        </transition>

        <transition name="fade">
          <div v-if="error" class="alert alert-error">{{ error }}</div>
        </transition>

        <form v-if="!success" @submit.prevent="handleCancel">
          <div class="form-group">
            <label class="form-label">Código de cancelación</label>
            <input
              v-model="cancelCode"
              class="form-control"
              type="text"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              required
              :disabled="loading"
            />
          </div>
          <button type="submit" class="btn btn-danger btn-full" :disabled="loading || !cancelCode.trim()">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Cancelando...' : 'Confirmar Cancelación' }}
          </button>
        </form>

        <div v-if="success" style="margin-top:1rem; text-align:center">
          <router-link to="/" class="btn btn-primary">Hacer nueva reserva</router-link>
        </div>
      </div>
    </div>
  </PublicLayout>
</template>

<script setup>
import { ref } from 'vue'
import PublicLayout from '../components/PublicLayout.vue'
import { reservationApi } from '../api'

const cancelCode = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleCancel() {
  error.value = ''
  loading.value = true
  try {
    await reservationApi.cancelReservation(cancelCode.value.trim())
    success.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || 'Código inválido o reserva no encontrada.'
  } finally {
    loading.value = false
  }
}
</script>
