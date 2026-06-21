import { defineStore } from 'pinia'
import type { User } from '~/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    setTokens(access: string, refresh: string, user: User) {
      this.accessToken = access
      this.refreshToken = refresh
      this.user = user
      if (import.meta.client) {
        localStorage.setItem('lumia_access', access)
        localStorage.setItem('lumia_refresh', refresh)
        localStorage.setItem('lumia_user', JSON.stringify(user))
      }
    },

    loadFromStorage() {
      if (import.meta.client) {
        this.accessToken = localStorage.getItem('lumia_access')
        this.refreshToken = localStorage.getItem('lumia_refresh')
        const user = localStorage.getItem('lumia_user')
        if (user) this.user = JSON.parse(user)
      }
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      if (import.meta.client) {
        localStorage.removeItem('lumia_access')
        localStorage.removeItem('lumia_refresh')
        localStorage.removeItem('lumia_user')
      }
    },
  },
})
