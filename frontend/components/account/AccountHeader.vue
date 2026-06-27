<template>
  <div class="bg-white rounded-3xl border border-base-200 shadow-sm p-4 sm:p-5">
    <div class="flex items-start justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0">
        <div
          class="w-12 h-12 sm:w-14 sm:h-14 rounded-2xl bg-primary/15 text-primary flex items-center justify-center shrink-0 font-bold text-lg"
          aria-hidden="true"
        >
          <span v-if="initials">{{ initials }}</span>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <div class="min-w-0">
          <h1 class="font-bold text-lg sm:text-xl text-lumia-dark truncate">{{ displayName }}</h1>
          <p class="text-sm text-base-content/60 truncate" dir="ltr">{{ phone }}</p>
        </div>
      </div>
      <button
        type="button"
        class="btn btn-outline btn-sm rounded-full gap-1.5 shrink-0"
        @click="emit('logout')"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        خروج
      </button>
    </div>

    <div class="flex flex-wrap gap-2 mt-4 pt-4 border-t border-base-200">
      <NuxtLink to="/shop" class="quick-link">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
        </svg>
        فروشگاه
      </NuxtLink>
      <button type="button" class="quick-link" @click="onCartClick">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        سبد خرید
        <span v-if="cartCount" class="badge badge-primary badge-xs">{{ cartCount }}</span>
      </button>
      <NuxtLink to="/contact" class="quick-link">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        پشتیبانی
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCartStore } from '~/stores/cart'

const props = defineProps<{
  displayName: string
  phone?: string
  firstName?: string
  lastName?: string
}>()

const emit = defineEmits<{ logout: [] }>()

const cart = useCartStore()
const router = useRouter()

const cartCount = computed(() => cart.itemCount)

const initials = computed(() => {
  const first = props.firstName?.trim()?.[0] || ''
  const last = props.lastName?.trim()?.[0] || ''
  const combined = (first + last).toUpperCase()
  return combined || ''
})

function onCartClick() {
  if (cart.itemCount > 0) {
    cart.openDrawer()
  } else {
    router.push('/shop')
  }
}
</script>

<style scoped>
.quick-link {
  @apply inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs sm:text-sm font-medium
    bg-base-100 border border-base-200 text-base-content
    hover:border-primary/40 hover:text-primary transition-colors;
}
</style>
