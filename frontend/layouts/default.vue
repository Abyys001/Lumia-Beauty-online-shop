<template>
  <div data-theme="lumia" class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
    <FloatingWhatsApp />
    <PwaInstallBanner />
    <MobileNav />
    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

const cart = useCartStore()
const auth = useAuthStore()
onMounted(() => {
  if (auth.isAuthenticated) {
    cart.fetchCart()
  }
})
</script>
