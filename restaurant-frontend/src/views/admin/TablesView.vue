<template>
  <div>
    <div class="page-header">
      <h2>Gestión de Mesas</h2>
      <button class="btn btn-primary" @click="openModal()">+ Nueva Mesa</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div class="table-wrap">
      <div v-if="loading" style="padding:1.5rem; text-align:center;"><span class="spinner"></span></div>
      <table v-else>
        <thead>
          <tr><th>Número</th><th>Capacidad</th><th>Estado</th><th>Reservas futuras</th><th>Acciones</th></tr>
        </thead>
        <tbody>
          <tr v-if="!tables.length">
            <td colspan="5" style="text-align:center; color:var(--text-muted); padding:2rem;">No hay mesas registradas.</td>
          </tr>
          <tr v-for="t in tables" :key="t.id">
            <td><strong>#{{ t.number }}</strong></td>
            <td>{{ t.capacity }} personas</td>
            <td><span :class="['badge', t.is_active ? 'badge-success' : 'badge-error']">{{ t.is_active ? 'Activa' : 'Inactiva' }}</span></td>
            <td>{{ t.has_future_reservations ? 'Sí' : 'No' }}</td>
            <td class="actions-cell">
              <button class="btn btn-secondary btn-sm" @click="openModal(t)">Editar</button>
              <button class="btn btn-danger btn-sm" @click="deleteTable(t)" :disabled="t.has_future_reservations">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal card">
        <h3>{{ editingTable ? 'Editar Mesa' : 'Nueva Mesa' }}</h3>
        <hr class="divider" />
        <div v-if="modalError" class="alert alert-error">{{ modalError }}</div>
        <form @submit.prevent="saveTable">
          <div class="form-group">
            <label class="form-label">Número / Código *</label>
            <input v-model="form.number" class="form-control" type="text" placeholder="Ej: T1, Mesa 5" required />
          </div>
          <div class="form-group">
            <label class="form-label">Capacidad (personas) *</label>
            <input v-model.number="form.capacity" class="form-control" type="number" min="1" max="20" required />
          </div>
          <div class="form-group">
            <label class="form-label">Estado</label>
            <select v-model="form.is_active" class="form-control">
              <option :value="true">Activa</option>
              <option :value="false">Inactiva</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancelar</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner"></span>
              {{ saving ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api'

const tables = ref([])
const loading = ref(false)
const error = ref('')
const showModal = ref(false)
const editingTable = ref(null)
const saving = ref(false)
const modalError = ref('')
const form = ref({ number: '', capacity: 4, is_active: true })

onMounted(loadTables)

async function loadTables() {
  loading.value = true
  try {
    const { data } = await adminApi.getTables()
    tables.value = Array.isArray(data) ? data : (data.results || [])
  } catch { error.value = 'Error al cargar mesas.' }
  finally { loading.value = false }
}

function openModal(table = null) {
  editingTable.value = table
  form.value = table ? { number: table.number, capacity: table.capacity, is_active: table.is_active } : { number: '', capacity: 4, is_active: true }
  modalError.value = ''
  showModal.value = true
}
function closeModal() { showModal.value = false }

async function saveTable() {
  modalError.value = ''
  saving.value = true
  try {
    if (editingTable.value) {
      await adminApi.updateTable(editingTable.value.id, form.value)
    } else {
      await adminApi.createTable(form.value)
    }
    closeModal()
    await loadTables()
  } catch (err) {
    modalError.value = err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Error al guardar.'
  } finally { saving.value = false }
}

async function deleteTable(table) {
  if (!confirm(`¿Eliminar mesa ${table.number}?`)) return
  try {
    await adminApi.deleteTable(table.id)
    await loadTables()
  } catch (err) {
    error.value = err.response?.data?.detail || 'No se puede eliminar la mesa.'
  }
}
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.actions-cell { display: flex; gap: 0.5rem; }
.modal-overlay { background: rgba(0,0,0,0.7); bottom: 0; display: flex; left: 0; position: fixed; right: 0; top: 0; z-index: 500; align-items: center; justify-content: center; }
.modal { max-width: 440px; width: 90%; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1rem; }
</style>
