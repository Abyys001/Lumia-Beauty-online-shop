import { defineStore } from 'pinia'
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
      } finally {
        this.loading = false
      }
    },

    async addItem(productId: string, quantity = 1) {
      const { apiFetch } = useApi()
      this.cart = await apiFetch<Cart>('/cart/', {
        method: 'POST',
        body: { product_id: productId, quantity },
      })
      this.drawerOpen = true
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
