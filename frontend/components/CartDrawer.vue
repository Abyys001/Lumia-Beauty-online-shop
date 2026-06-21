<template>
  <div class="drawer drawer-end z-50">
    <input
      id="cart-drawer"
      type="checkbox"
      class="drawer-toggle"
      :checked="cart.drawerOpen"
      @change="cart.drawerOpen = ($event.target as HTMLInputElement).checked"
    />
    <div class="drawer-side">
      <label class="drawer-overlay" @click="cart.closeDrawer()" />
      <div class="menu p-0 w-80 sm:w-96 min-h-full bg-base-100 text-base-content flex flex-col">
        <div class="p-4 border-b border-base-200 flex items-center justify-between">
          <h3 class="font-bold text-lg">سبد خرید</h3>
          <button class="btn btn-ghost btn-sm btn-circle" @click="cart.closeDrawer()">✕</button>
        </div>

        <div v-if="cart.loading" class="flex-1 flex items-center justify-center">
          <span class="loading loading-spinner" />
        </div>

        <div v-else-if="!cart.items.length" class="flex-1 flex flex-col items-center justify-center p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-base-content/20 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
          </svg>
          <p class="text-base-content/50">سبد خرید شما خالی است</p>
          <NuxtLink to="/shop" class="btn btn-primary btn-sm mt-4 rounded-full" @click="cart.closeDrawer()">
            مشاهده محصولات
          </NuxtLink>
        </div>

        <template v-else>
          <ul class="flex-1 overflow-y-auto p-4 space-y-4">
            <li
              v-for="item in cart.items"
              :key="item.id"
              class="flex gap-3"
            >
              <img
                v-if="item.product.primary_image"
                :src="item.product.primary_image"
                :alt="item.product.name"
                class="w-16 h-16 rounded-xl object-cover"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ item.product.name }}</p>
                <p class="text-xs text-primary">{{ formatPrice(item.subtotal) }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <button
                    class="btn btn-xs btn-circle btn-outline"
                    @click="cart.updateItem(item.id, item.quantity - 1)"
                  >
                    −
                  </button>
                  <span class="text-sm w-6 text-center">{{ item.quantity }}</span>
                  <button
                    class="btn btn-xs btn-circle btn-outline"
                    @click="cart.updateItem(item.id, item.quantity + 1)"
                  >
                    +
                  </button>
                </div>
              </div>
            </li>
          </ul>

          <div class="p-4 border-t border-base-200 space-y-3">
            <div class="flex justify-between font-bold">
              <span>جمع کل</span>
              <span class="text-primary">{{ formatPrice(cart.total) }}</span>
            </div>
            <NuxtLink to="/cart" class="btn btn-outline w-full rounded-full" @click="cart.closeDrawer()">
              مشاهده سبد
            </NuxtLink>
            <NuxtLink to="/checkout" class="btn btn-primary w-full rounded-full" @click="cart.closeDrawer()">
              تسویه حساب
            </NuxtLink>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const cart = useCartStore()
const { formatPrice } = useApi()
</script>
