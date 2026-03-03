<template>
  <PublicLayout>
    <div class="home-hero">
      <div class="hero-content">
        <div class="gold-line"></div>
        <h1>Reserva tu Mesa<br /><span class="accent">esta Noche</span></h1>
        <p class="hero-sub">Elige fecha, hora y número de comensales. Te asignamos la mejor mesa disponible.</p>
      </div>
    </div>

    <div class="container home-body">
      <!-- Availability Checker + Form -->
      <div class="form-wrapper">
        <div class="card form-card">
          <h2>Nueva Reserva</h2>
          <p class="form-desc">Completa los datos para reservar tu mesa.</p>
          <hr class="divider" />

          <form @submit.prevent="handleSubmit" novalidate>
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Nombre completo *</label>
                <input v-model="form.name" class="form-control" type="text" placeholder="Juan García" required :disabled="submitting" />
                <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
              </div>
              <div class="form-group">
                <label class="form-label">Email *</label>
                <input v-model="form.email" class="form-control" type="email" placeholder="juan@ejemplo.com" required :disabled="submitting" />
                <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Teléfono *</label>
                <input v-model="form.phone" class="form-control" type="tel" placeholder="6000 0000" required :disabled="submitting" />
                <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
              </div>
              <div class="form-group">
                <label class="form-label">Número de personas *</label>
                <input v-model.number="form.guests" class="form-control" type="number" min="1" max="20" placeholder="2" required :disabled="submitting" />
                <span v-if="errors.guests" class="field-error">{{ errors.guests }}</span>
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Fecha *</label>
                <input v-model="form.date" class="form-control" type="date" :min="minDate" required :disabled="submitting" @change="onDateOrGuestsChange" />
                <span v-if="errors.date" class="field-error">{{ errors.date }}</span>
              </div>
              <div class="form-group">
                <label class="form-label">Hora *</label>
                <select v-model="form.time" class="form-control" required :disabled="submitting || loadingSlots || !availableSlots.length">
                  <option value="" disabled>
                    {{ loadingSlots ? 'Consultando...' : (form.date ? (availableSlots.length ? 'Selecciona hora' : 'Sin disponibilidad') : 'Elige fecha primero') }}
                  </option>
                  <option v-for="slot in availableSlots" :key="slot.time" :value="slot.time">
                    {{ slot.time }} ({{ slot.available_tables }} mesa{{ slot.available_tables !== 1 ? 's' : '' }} disponible{{ slot.available_tables !== 1 ? 's' : '' }})
                  </option>
                </select>
                <span v-if="errors.time" class="field-error">{{ errors.time }}</span>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Notas (opcional)</label>
              <textarea v-model="form.notes" class="form-control" rows="2" placeholder="Alergias, ocasión especial, etc." :disabled="submitting"></textarea>
            </div>

            <!-- Availability note -->
            <transition name="fade">
              <div v-if="availabilityMessage" :class="['alert', availabilityMessage.type === 'error' ? 'alert-error' : 'alert-warning']">
                {{ availabilityMessage.text }}
              </div>
            </transition>

            <!-- API error -->
            <transition name="fade">
              <div v-if="apiError" class="alert alert-error">{{ apiError }}</div>
            </transition>

            <button type="submit" class="btn btn-primary btn-full" :disabled="submitting || !form.time">
              <span v-if="submitting" class="spinner"></span>
              {{ submitting ? 'Reservando...' : 'Confirmar Reserva' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </PublicLayout>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'
import { reservationApi } from '../api'

const router = useRouter()

const form = ref({ name: '', email: '', phone: '', date: '', time: '', guests: 2, notes: '' })
const errors = ref({})
const apiError = ref('')
const submitting = ref(false)
const loadingSlots = ref(false)
const availableSlots = ref([])
const availabilityMessage = ref(null)

const minDate = computed(() => {
  const today = new Date()
  today.setDate(today.getDate() + 1)
  return today.toISOString().split('T')[0]
})

function validateForm() {
  const e = {}
  if (!form.value.name.trim()) e.name = 'El nombre es obligatorio.'
  if (!form.value.email.trim()) e.email = 'El email es obligatorio.'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) e.email = 'Email inválido.'
  if (!form.value.phone.trim()) e.phone = 'El teléfono es obligatorio.'
  if (!form.value.date) e.date = 'La fecha es obligatoria.'
  if (!form.value.time) e.time = 'La hora es obligatoria.'
  if (!form.value.guests || form.value.guests < 1) e.guests = 'Mínimo 1 persona.'
  errors.value = e
  return Object.keys(e).length === 0
}

async function fetchAvailability() {
  if (!form.value.date || !form.value.guests) return
  loadingSlots.value = true
  availableSlots.value = []
  form.value.time = ''
  availabilityMessage.value = null

  try {
    const { data } = await reservationApi.getAvailability(form.value.date, form.value.guests)
    availableSlots.value = data.available_slots || []
    if (!availableSlots.value.length) {
      availabilityMessage.value = { type: 'warning', text: 'No hay disponibilidad para la fecha y personas seleccionadas.' }
    }
  } catch (err) {
    availabilityMessage.value = { type: 'error', text: err.response?.data?.detail || 'Error al consultar disponibilidad.' }
  } finally {
    loadingSlots.value = false
  }
}

function onDateOrGuestsChange() {
  if (form.value.date && form.value.guests) fetchAvailability()
}

watch(() => form.value.guests, () => {
  if (form.value.date) fetchAvailability()
})

async function handleSubmit() {
  apiError.value = ''
  if (!validateForm()) return

  submitting.value = true
  try {
    const { data } = await reservationApi.createReservation({
      name: form.value.name,
      email: form.value.email,
      phone: form.value.phone,
      date: form.value.date,
      time: form.value.time,
      guests: form.value.guests,
      notes: form.value.notes,
    })
    router.push({ name: 'confirmation', state: { reservation: data } })
  } catch (err) {
    apiError.value = err.response?.data?.detail || 'Error al crear la reserva. Por favor intenta de nuevo.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.home-hero {
  background: linear-gradient(135deg, #1a1208 0%, #0f0d0a 60%),
              url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="%23d4a84320" stroke-width="0.5"/></svg>');
  padding: 5rem 1.5rem 4rem;
  text-align: center;
}
.hero-content { max-width: 650px; margin: 0 auto; }
.hero-content .gold-line { margin: 0 auto 1.5rem; }
.accent { color: var(--primary); }
.hero-sub { font-size: 1.1rem; margin-top: 1rem; color: var(--text-muted); }
.home-body { padding: 3rem 1.5rem; }
.form-wrapper { max-width: 780px; margin: 0 auto; }
.form-card h2 { margin-bottom: 0.25rem; }
.form-desc { margin-bottom: 0; font-size: 0.9rem; }
.field-error { color: var(--error); font-size: 0.8rem; margin-top: 0.2rem; }
</style>
