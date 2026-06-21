<template>
  <div data-theme="lumia" class="min-h-screen flex flex-col">
    <AppHeader />
    <main class="flex-1">
      <slot />
    </main>
    <AppFooter />
    <CartDrawer />
  </div>
</template>

<script setup lang="ts">
const cart = useCartStore()
onMounted(() => {
  cart.fetchCart()
})
</script>
