import { defineStore } from 'pinia'
import { isAccessTokenExpired } from '~/utils/jwt'
import type { User } from '~/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
    hydrated: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async refreshAccessToken(): Promise<boolean> {
      if (!this.refreshToken || !import.meta.client) return false
      if (isAccessTokenExpired(this.refreshToken)) return false
      const config = useRuntimeConfig()
      try {
        const result = await $fetch<{ access: string }>('/auth/token/refresh/', {
          baseURL: config.public.apiBase,
          method: 'POST',
          body: { refresh: this.refreshToken },
        })
        this.accessToken = result.access
        localStorage.setItem('lumia_access', result.access)
        return true
      } catch {
        return false
      }
    },

    setTokens(access: string, refresh: string, user: User) {
      this.accessToken = access
      this.refreshToken = refresh
      this.user = user
      if (import.meta.client) {
        localStorage.setItem('lumia_access', access)
        localStorage.setItem('lumia_refresh', refresh)
        localStorage.setItem('lumia_user', JSON.stringify(user))
        useCartStore().fetchCart().catch(() => {})
      }
    },

    loadFromStorage() {
      if (import.meta.client) {
        this.accessToken = localStorage.getItem('lumia_access')
        this.refreshToken = localStorage.getItem('lumia_refresh')
        const user = localStorage.getItem('lumia_user')
        if (user) {
          try {
            this.user = JSON.parse(user)
          } catch {
            this.user = null
          }
        }
      }
    },

    async hydrateSession() {
      if (!import.meta.client) return
      this.loadFromStorage()

      if (!this.accessToken && !this.refreshToken) {
        this.hydrated = true
        return
      }

      if (!this.refreshToken || isAccessTokenExpired(this.refreshToken)) {
        this.logout()
        this.hydrated = true
        return
      }

      if (!this.accessToken || isAccessTokenExpired(this.accessToken)) {
        const refreshed = await this.refreshAccessToken()
        if (!refreshed) {
          this.logout()
        }
      }

      this.hydrated = true
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
      useWishlistStore().reset()
    },
  },
})
