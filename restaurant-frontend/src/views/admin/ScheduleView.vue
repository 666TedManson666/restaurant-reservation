<template>
  <div>
    <h2 style="margin-bottom:1.5rem;">Configuración de Horarios</h2>

    <div v-if="loading" style="text-align:center; padding:2rem;"><span class="spinner"></span></div>

    <div v-else class="card" style="max-width:560px;">
      <div v-if="success" class="alert alert-success">✓ Horario actualizado correctamente.</div>
      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="saveSchedule">
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Hora de apertura *</label>
            <input v-model="form.opening_time" class="form-control" type="time" required />
          </div>
          <div class="form-group">
            <label class="form-label">Hora de cierre *</label>
            <input v-model="form.closing_time" class="form-control" type="time" required />
          </div>
        </div>
        <div class="grid-2">
          <div class="form-group">
            <label class="form-label">Intervalo entre turnos (min) *</label>
            <select v-model.number="form.slot_interval_minutes" class="form-control">
              <option :value="30">30 minutos</option>
              <option :value="60">60 minutos</option>
              <option :value="90">90 minutos</option>
              <option :value="120">2 horas</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Duración de reserva (min) *</label>
            <select v-model.number="form.reservation_duration_minutes" class="form-control">
              <option :value="60">60 minutos (1h)</option>
              <option :value="90">90 minutos (1h 30m)</option>
              <option :value="120">120 minutos (2h)</option>
            </select>
          </div>
        </div>

        <!-- Slots Preview -->
        <div v-if="schedule?.available_slots?.length" class="slots-preview">
          <p class="slots-title">Turnos disponibles según configuración actual:</p>
          <div class="slots-list">
            <span v-for="slot in schedule.available_slots" :key="slot" class="slot-chip">{{ slot }}</span>
          </div>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner"></span>
          {{ saving ? 'Guardando...' : 'Guardar Horario' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref(false)
const schedule = ref(null)
const form = ref({ opening_time: '12:00', closing_time: '23:00', slot_interval_minutes: 60, reservation_duration_minutes: 90 })

onMounted(async () => {
  try {
    const { data } = await adminApi.getSchedule()
    schedule.value = data
    form.value = {
      opening_time: data.opening_time,
      closing_time: data.closing_time,
      slot_interval_minutes: data.slot_interval_minutes,
      reservation_duration_minutes: data.reservation_duration_minutes,
    }
  } catch { error.value = 'Error al cargar el horario.' }
  finally { loading.value = false }
})

async function saveSchedule() {
  error.value = ''
  success.value = false
  saving.value = true
  try {
    const { data } = await adminApi.updateSchedule(form.value)
    schedule.value = data
    success.value = true
    setTimeout(() => { success.value = false }, 3000)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Error al guardar el horario.'
  } finally { saving.value = false }
}
</script>

<style scoped>
.slots-preview { background: var(--bg-card2); border-radius: 8px; margin: 1rem 0; padding: 1rem; }
.slots-title { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem; }
.slots-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.slot-chip { background: rgba(212,168,67,0.12); border: 1px solid var(--border); border-radius: 20px; color: var(--primary); font-size: 0.8rem; font-weight: 600; padding: 0.2rem 0.75rem; }
</style>
