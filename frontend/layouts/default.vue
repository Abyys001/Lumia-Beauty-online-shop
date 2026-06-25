<template>
  <div data-theme="lumia" class="min-h-screen flex flex-col overflow-x-clip w-full max-w-[100vw]">
    <AppHeader />
    <main class="flex-1 min-w-0 max-w-full overflow-x-clip">
      <div v-if="back" class="container-lumia pt-3 pb-0">
        <PageBack />
      </div>
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
const { back } = usePageBack()
onMounted(async () => {
  if (!auth.hydrated) {
    await auth.hydrateSession()
  }
  if (!auth.isAuthenticated) return
  try {
    await cart.fetchCart()
  } catch {
    // Ignore stale-session cart errors; user can log in again.
  }
})
</script>
