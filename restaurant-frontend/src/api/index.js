import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auto-refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (!refreshToken) throw new Error('No refresh token')
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/token/refresh/`,
          { refresh: refreshToken }
        )
        localStorage.setItem('access_token', data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/admin/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ─── Public endpoints ────────────────────────────────────────────────────────
export const reservationApi = {
  getAvailability: (date, guests) =>
    api.get('/availability/', { params: { date, guests } }),
  createReservation: (data) => api.post('/reservations/', data),
  cancelReservation: (cancelCode) =>
    api.post('/reservations/cancel/', { cancel_code: cancelCode }),
}

// ─── Admin endpoints ─────────────────────────────────────────────────────────
export const adminApi = {
  login: (username, password) =>
    axios.post(
      `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/token/`,
      { username, password }
    ),
  // Tables
  getTables: () => api.get('/admin/tables/'),
  createTable: (data) => api.post('/admin/tables/', data),
  updateTable: (id, data) => api.put(`/admin/tables/${id}/`, data),
  deleteTable: (id) => api.delete(`/admin/tables/${id}/`),
  // Schedule
  getSchedule: () => api.get('/admin/schedule/'),
  updateSchedule: (data) => api.patch('/admin/schedule/', data),
  // Reservations
  getReservations: (params) => api.get('/admin/reservations/', { params }),
  cancelReservation: (id) => api.post(`/admin/reservations/${id}/cancel/`),
  // Metrics
  getMetrics: (date) => api.get('/admin/metrics/', { params: { date } }),
}
