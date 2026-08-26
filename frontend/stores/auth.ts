import { defineStore } from 'pinia'
import { isAccessTokenExpired } from '~/utils/jwt'
import type { TrustedDeviceGrant, User } from '~/types'
import { resolveClientApiBase } from '~/utils/apiBase'

const DEVICE_KEY = 'lumia_device'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
    device: null as TrustedDeviceGrant | null,
    hydrated: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isDeviceRemembered: (state) => !!state.device,
  },

  actions: {
    async refreshAccessToken(): Promise<boolean> {
      if (!this.refreshToken || !import.meta.client) return false
      if (isAccessTokenExpired(this.refreshToken)) return false
      const config = useRuntimeConfig()
      try {
        const result = await $fetch<{ access: string }>('/auth/token/refresh/', {
          baseURL: resolveClientApiBase(config.public.apiBase),
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

    setTokens(access: string, refresh: string, user: User, device?: TrustedDeviceGrant | null) {
      this.accessToken = access
      this.refreshToken = refresh
      this.user = user
      if (device !== undefined) this.setDevice(device)
      if (import.meta.client) {
        localStorage.setItem('lumia_access', access)
        localStorage.setItem('lumia_refresh', refresh)
        localStorage.setItem('lumia_user', JSON.stringify(user))
        useCartStore().fetchCart().catch(() => {})
      }
    },

    /**
     * The device secret is single-use: the server hands back a replacement on
     * every auto-login, and losing it costs the customer their auto-login, so
     * it is written before anything else can throw.
     */
    setDevice(device: TrustedDeviceGrant | null) {
      this.device = device
      if (!import.meta.client) return
      if (device) localStorage.setItem(DEVICE_KEY, JSON.stringify(device))
      else localStorage.removeItem(DEVICE_KEY)
    },

    loadDevice(): TrustedDeviceGrant | null {
      if (!import.meta.client) return null
      const raw = localStorage.getItem(DEVICE_KEY)
      if (!raw) return null
      try {
        const parsed = JSON.parse(raw) as TrustedDeviceGrant
        this.device = parsed.id && parsed.token ? parsed : null
      } catch {
        this.device = null
      }
      return this.device
    },

    /** Sign in from a remembered browser — no password, no redirect to /auth. */
    async tryDeviceLogin(): Promise<boolean> {
      const device = this.loadDevice()
      if (!device) return false
      const config = useRuntimeConfig()
      try {
        const result = await $fetch<{
          access: string
          refresh: string
          user: User
          device: TrustedDeviceGrant
        }>('/auth/device/login/', {
          baseURL: resolveClientApiBase(config.public.apiBase),
          method: 'POST',
          body: { device_id: device.id, device_token: device.token },
        })
        this.setTokens(result.access, result.refresh, result.user, result.device)
        return true
      } catch (error) {
        // 401 means the grant is spent, expired or revoked — never retry it.
        if ((error as { statusCode?: number }).statusCode === 401) this.setDevice(null)
        return false
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

      this.loadDevice()

      if (!this.accessToken && !this.refreshToken) {
        await this.tryDeviceLogin()
        this.hydrated = true
        return
      }

      if (!this.refreshToken || isAccessTokenExpired(this.refreshToken)) {
        this.logout(false)
        await this.tryDeviceLogin()
        this.hydrated = true
        return
      }

      if (!this.accessToken || isAccessTokenExpired(this.accessToken)) {
        const refreshed = await this.refreshAccessToken()
        if (!refreshed) {
          this.logout(false)
          await this.tryDeviceLogin()
        }
      }

      this.hydrated = true
    },

    /**
     * `forgetDevice` defaults to true because an explicit sign-out should stop
     * auto-login; an expiry-driven logout passes false so the remembered device
     * can sign the customer straight back in.
     */
    logout(forgetDevice = true) {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      if (import.meta.client) {
        localStorage.removeItem('lumia_access')
        localStorage.removeItem('lumia_refresh')
        localStorage.removeItem('lumia_user')
      }
      if (forgetDevice) this.setDevice(null)
      useWishlistStore().reset()
    },

    /** Explicit sign-out: tells the server to drop this device first. */
    async signOut(everywhere = false) {
      const device = this.device
      if (this.accessToken) {
        const { apiFetch } = useApi()
        await apiFetch('/auth/logout/', {
          method: 'POST',
          body: { device_id: device?.id ?? null, everywhere },
        }).catch(() => {})
      }
      this.logout()
    },
  },
})
