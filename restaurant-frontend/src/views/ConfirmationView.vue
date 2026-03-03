<template>
  <PublicLayout>
    <div class="page-center">
      <div class="card confirmation-card" style="max-width:560px; width:100%">
        <div class="success-icon">✓</div>
        <h2>¡Reserva Confirmada!</h2>
        <p>Tu mesa ha sido reservada exitosamente.</p>
        <hr class="divider" />

        <div v-if="reservation" class="details-grid">
          <div class="detail-item"><span class="detail-label">Nombre</span><span>{{ reservation.name }}</span></div>
          <div class="detail-item"><span class="detail-label">Fecha</span><span>{{ formatDate(reservation.date) }}</span></div>
          <div class="detail-item"><span class="detail-label">Hora</span><span>{{ reservation.time }}</span></div>
          <div class="detail-item"><span class="detail-label">Personas</span><span>{{ reservation.guests }}</span></div>
          <div class="detail-item"><span class="detail-label">Mesa</span><span>#{{ reservation.table_number }}</span></div>
          <div class="detail-item"><span class="detail-label">Estado</span><span class="badge badge-success">Confirmada</span></div>
        </div>

        <div class="cancel-code-box">
          <p class="cancel-label">Código de cancelación (guárdalo)</p>
          <code class="cancel-code">{{ reservation?.cancel_code }}</code>
        </div>

        <div class="actions">
          <router-link to="/" class="btn btn-primary">Hacer otra reserva</router-link>
          <router-link to="/cancel" class="btn btn-secondary">Cancelar reserva</router-link>
        </div>
      </div>
    </div>
  </PublicLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import PublicLayout from '../components/PublicLayout.vue'

const router = useRouter()
const reservation = computed(() => history.state?.reservation || null)

if (!reservation.value) router.push('/')

function formatDate(d) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  return `${day}/${m}/${y}`
}
</script>

<style scoped>
.confirmation-card { text-align: center; }
.success-icon {
  background: rgba(74,222,128,0.15);
  border: 2px solid var(--success);
  border-radius: 50%;
  color: var(--success);
  font-size: 2rem;
  font-weight: 700;
  height: 64px;
  line-height: 60px;
  margin: 0 auto 1.25rem;
  width: 64px;
}
.details-grid { display: grid; gap: 0.5rem 1.5rem; grid-template-columns: 1fr 1fr; margin: 1rem 0; text-align: left; }
.detail-item { display: flex; flex-direction: column; }
.detail-label { color: var(--text-muted); font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.cancel-code-box { background: var(--bg-card2); border: 1px dashed var(--primary); border-radius: 8px; margin: 1.25rem 0; padding: 1rem; }
.cancel-label { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.cancel-code { color: var(--primary); font-size: 0.85rem; word-break: break-all; letter-spacing: 0.05em; }
.actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-top: 0.5rem; }
</style>
