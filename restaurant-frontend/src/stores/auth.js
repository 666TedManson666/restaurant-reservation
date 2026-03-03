import { defineStore } from 'pinia'
import { adminApi } from '../api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
    }),

    getters: {
        isAuthenticated: (state) => !!state.accessToken,
    },

    actions: {
        async login(username, password) {
            const { data } = await adminApi.login(username, password)
            this.accessToken = data.access
            this.refreshToken = data.refresh
            localStorage.setItem('access_token', data.access)
            localStorage.setItem('refresh_token', data.refresh)
        },

        logout() {
            this.accessToken = null
            this.refreshToken = null
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
        },
    },
})
