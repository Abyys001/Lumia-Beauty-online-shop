import { defineStore } from 'pinia'
import { isUnauthorizedError } from '~/utils/jwt'
import type { Product } from '~/types'

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    ids: [] as string[],
    products: [] as Product[],
    loaded: false,
    loading: false,
  }),

  getters: {
    has: (state) => (productId: string) => state.ids.includes(productId),
    count: (state) => state.ids.length,
  },

  actions: {
    async loadIds() {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        this.reset()
        return
      }
      const { apiFetch } = useApi()
      try {
        this.ids = await apiFetch<string[]>('/user/wishlist/ids/')
        this.loaded = true
      } catch (error) {
        if (isUnauthorizedError(error)) {
          this.reset()
          return
        }
        throw error
      }
    },

    async loadProducts() {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) return
      const { apiFetch } = useApi()
      this.loading = true
      try {
        this.products = await apiFetch<Product[]>('/user/wishlist/')
        this.ids = this.products.map(p => p.id)
        this.loaded = true
      } catch (error) {
        if (isUnauthorizedError(error)) {
          this.reset()
          return
        }
        throw error
      } finally {
        this.loading = false
      }
    },

    async toggle(productId: string) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        await navigateTo('/auth')
        return
      }
      const { apiFetch } = useApi()
      if (this.has(productId)) {
        await apiFetch(`/user/wishlist/${productId}/`, { method: 'DELETE' })
        this.ids = this.ids.filter(id => id !== productId)
        this.products = this.products.filter(p => p.id !== productId)
      } else {
        await apiFetch('/user/wishlist/', { method: 'POST', body: { product_id: productId } })
        this.ids.push(productId)
      }
    },

    reset() {
      this.ids = []
      this.products = []
      this.loaded = false
    },
  },
})
