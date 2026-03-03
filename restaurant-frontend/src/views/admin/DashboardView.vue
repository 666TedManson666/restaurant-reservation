<template>
  <div>
    <div class="dash-header">
      <h2>Dashboard</h2>
      <div class="date-picker-row">
        <input v-model="selectedDate" type="date" class="form-control date-input" @change="loadAll" />
      </div>
    </div>

    <!-- Metrics -->
    <div class="metrics-grid" v-if="!loadingMetrics">
      <div class="metric-card">
        <span class="metric-icon">✅</span>
        <div class="metric-value">{{ metrics.confirmed_reservations }}</div>
        <div class="metric-label">Confirmadas</div>
      </div>
      <div class="metric-card">
        <span class="metric-icon">❌</span>
        <div class="metric-value">{{ metrics.cancelled_reservations }}</div>
        <div class="metric-label">Canceladas</div>
      </div>
      <div class="metric-card">
        <span class="metric-icon">🪑</span>
        <div class="metric-value">{{ metrics.total_active_tables }}</div>
        <div class="metric-label">Mesas Activas</div>
      </div>
      <div class="metric-card">
        <span class="metric-icon">📊</span>
        <div class="metric-value">{{ metrics.occupancy_percentage }}%</div>
        <div class="metric-label">Ocupación</div>
        <div class="occupancy-bar">
          <div class="occupancy-fill" :style="{ width: metrics.occupancy_percentage + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-row">
      <select v-model="statusFilter" class="form-control filter-select" @change="loadReservations">
        <option value="">Todos los estados</option>
        <option value="confirmed">Confirmadas</option>
        <option value="cancelled">Canceladas</option>
      </select>
    </div>

    <!-- Reservations table -->
    <div class="table-wrap">
      <div v-if="loadingReservations" style="padding:1.5rem; text-align:center;">
        <span class="spinner"></span> Cargando reservas...
      </div>
      <table v-else>
        <thead>
          <tr>
            <th>ID</th><th>Nombre</th><th>Email</th><th>Hora</th><th>Personas</th><th>Mesa</th><th>Estado</th><th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!reservations.length">
            <td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">
              No hay reservas para esta fecha.
            </td>
          </tr>
          <tr v-for="r in reservations" :key="r.id">
            <td>#{{ r.id }}</td>
            <td>{{ r.name }}</td>
            <td>{{ r.email }}</td>
            <td>{{ r.time }}</td>
            <td>{{ r.guests }}</td>
            <td>Mesa {{ r.table_number }}</td>
            <td><span :class="['badge', r.status === 'confirmed' ? 'badge-success' : 'badge-error']">{{ r.status === 'confirmed' ? 'Confirmada' : 'Cancelada' }}</span></td>
            <td>
              <button v-if="r.status === 'confirmed'" class="btn btn-danger btn-sm" @click="cancelReservation(r.id)" :disabled="cancelling === r.id">
                <span v-if="cancelling === r.id" class="spinner"></span>
                Cancelar
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api'

const today = new Date().toISOString().split('T')[0]
const selectedDate = ref(today)
const statusFilter = ref('')
const metrics = ref({ confirmed_reservations: 0, cancelled_reservations: 0, total_active_tables: 0, occupancy_percentage: 0 })
const reservations = ref([])
const loadingMetrics = ref(false)
const loadingReservations = ref(false)
const cancelling = ref(null)

onMounted(loadAll)

async function loadAll() {
  await Promise.all([loadMetrics(), loadReservations()])
}

async function loadMetrics() {
  loadingMetrics.value = true
  try {
    const { data } = await adminApi.getMetrics(selectedDate.value)
    metrics.value = data
  } catch { /* ignore */ }
  finally { loadingMetrics.value = false }
}

async function loadReservations() {
  loadingReservations.value = true
  try {
    const params = { date: selectedDate.value }
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await adminApi.getReservations(params)
    reservations.value = Array.isArray(data) ? data : (data.results || [])
  } catch { reservations.value = [] }
  finally { loadingReservations.value = false }
}

async function cancelReservation(id) {
  cancelling.value = id
  try {
    await adminApi.cancelReservation(id)
    await loadAll()
  } catch { /* ignore */ }
  finally { cancelling.value = null }
}
</script>

<style scoped>
.dash-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap:wrap; gap:1rem; }
.date-input { width: auto; }
.metrics-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); margin-bottom: 1.5rem; }
@media (max-width: 900px) { .metrics-grid { grid-template-columns: repeat(2, 1fr); } }
.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  text-align: center;
}
.metric-icon { font-size: 1.5rem; }
.metric-value { font-size: 2rem; font-weight: 800; color: var(--primary); margin: 0.25rem 0; }
.metric-label { color: var(--text-muted); font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.occupancy-bar { background: var(--bg-card2); border-radius: 10px; height: 6px; margin-top: 0.75rem; overflow: hidden; }
.occupancy-fill { background: var(--primary); border-radius: 10px; height: 100%; transition: width 0.5s; }
.filters-row { margin-bottom: 1rem; }
.filter-select { width: 240px; }
</style>
