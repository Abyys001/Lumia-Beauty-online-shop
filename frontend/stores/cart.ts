import { defineStore } from 'pinia'
import { isUnauthorizedError } from '~/utils/jwt'
import type { Cart } from '~/types'

export const useCartStore = defineStore('cart', {
  state: () => ({
    cart: null as Cart | null,
    drawerOpen: false,
    loading: false,
  }),

  getters: {
    itemCount: (state) => state.cart?.item_count || 0,
    total: (state) => state.cart?.total || 0,
    items: (state) => state.cart?.items || [],
  },

  actions: {
    async fetchCart() {
      const { apiFetch } = useApi()
      this.loading = true
      try {
        this.cart = await apiFetch<Cart>('/cart/')
      } catch (error) {
        if (isUnauthorizedError(error)) {
          this.cart = null
          return
        }
        throw error
      } finally {
        this.loading = false
      }
    },

    async addItem(productId: string, quantity = 1): Promise<boolean> {
      // The cart lives on the server, so a guest must sign in first — otherwise the
      // 401 came back silently and the button looked broken.
      if (!await ensureAuthenticated()) return false

      const { apiFetch } = useApi()
      try {
        this.cart = await apiFetch<Cart>('/cart/', {
          method: 'POST',
          body: { product_id: productId, quantity },
        })
        this.drawerOpen = true
        return true
      } catch (error) {
        if (isUnauthorizedError(error)) {
          useAuthStore().logout()
          this.cart = null
          await ensureAuthenticated()
          return false
        }
        throw error
      }
    },

    async updateItem(itemId: string, quantity: number) {
      const { apiFetch } = useApi()
      this.cart = await apiFetch<Cart>(`/cart/items/${itemId}/`, {
        method: 'PATCH',
        body: { quantity },
      })
    },

    async removeItem(itemId: string) {
      const { apiFetch } = useApi()
      this.cart = await apiFetch<Cart>(`/cart/items/${itemId}/`, {
        method: 'DELETE',
      })
    },

    async clearCart() {
      const { apiFetch } = useApi()
      await apiFetch('/cart/', { method: 'DELETE' })
      this.cart = null
    },

    openDrawer() {
      this.drawerOpen = true
    },

    closeDrawer() {
      this.drawerOpen = false
    },
  },
})
