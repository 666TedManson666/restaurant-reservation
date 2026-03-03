import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import('../views/HomeView.vue'),
        meta: { title: 'Reservar Mesa' },
    },
    {
        path: '/confirmation',
        name: 'confirmation',
        component: () => import('../views/ConfirmationView.vue'),
        meta: { title: 'Reserva Confirmada' },
    },
    {
        path: '/cancel',
        name: 'cancel',
        component: () => import('../views/CancelView.vue'),
        meta: { title: 'Cancelar Reserva' },
    },
    {
        path: '/admin/login',
        name: 'admin-login',
        component: () => import('../views/admin/LoginView.vue'),
        meta: { title: 'Admin – Iniciar Sesión', guestOnly: true },
    },
    {
        path: '/admin',
        component: () => import('../views/admin/AdminLayout.vue'),
        meta: { requiresAuth: true },
        children: [
            {
                path: '',
                name: 'admin-dashboard',
                component: () => import('../views/admin/DashboardView.vue'),
                meta: { title: 'Panel de Administración' },
            },
            {
                path: 'tables',
                name: 'admin-tables',
                component: () => import('../views/admin/TablesView.vue'),
                meta: { title: 'Gestión de Mesas' },
            },
            {
                path: 'schedule',
                name: 'admin-schedule',
                component: () => import('../views/admin/ScheduleView.vue'),
                meta: { title: 'Horarios' },
            },
        ],
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

router.beforeEach((to, from, next) => {
    // Update page title
    document.title = `${to.meta.title || 'Restaurante'} | Mesa Reserva`

    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return next({ name: 'admin-login' })
    }
    if (to.meta.guestOnly && authStore.isAuthenticated) {
        return next({ name: 'admin-dashboard' })
    }
    next()
})

export default router
