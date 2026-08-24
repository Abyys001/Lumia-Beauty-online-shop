<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="cart.drawerOpen" class="fixed inset-0 z-[75]">
        <div class="absolute inset-0 bg-lumia-dark/40 backdrop-blur-xs" @click="cart.closeDrawer()" />

        <div class="absolute top-0 bottom-0 left-0 w-full max-w-sm bg-base-100 shadow-2xl flex flex-col animate-slide-in-ltr">
          <div class="p-4 border-b border-base-200 flex items-center justify-between">
            <h3 class="font-bold text-lg">سبد خرید</h3>
            <button class="btn btn-ghost btn-sm btn-circle" aria-label="بستن سبد" @click="cart.closeDrawer()">✕</button>
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
              <li v-for="item in cart.items" :key="item.id" class="flex gap-3">
                <img
                  v-if="item.product.primary_image"
                  :src="normalizeMediaUrl(item.product.primary_image) || item.product.primary_image"
                  :alt="item.product.name"
                  class="w-16 h-16 rounded-xl object-cover"
                />
                <div v-else class="w-16 h-16 rounded-xl bg-base-200 flex items-center justify-center shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7 text-base-content/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate">{{ item.product.name }}</p>
                  <p class="text-xs text-primary">{{ formatPrice(item.subtotal) }}</p>
                  <div class="flex items-center gap-2 mt-1">
                    <button
                      type="button"
                      class="btn btn-sm btn-circle"
                      :class="item.quantity === 1 ? 'btn-ghost text-error hover:bg-error/10' : 'btn-outline'"
                      :aria-label="item.quantity === 1 ? 'حذف از سبد' : 'کاهش تعداد'"
                      :disabled="busyItem === item.id"
                      @click="item.quantity === 1 ? changeItem(item.id, 0) : changeItem(item.id, item.quantity - 1)"
                    >
                      <svg
                        v-if="item.quantity === 1"
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <span v-else>−</span>
                    </button>
                    <span class="text-sm w-6 text-center">{{ item.quantity }}</span>
                    <button
                      type="button"
                      class="btn btn-sm btn-circle btn-outline"
                      aria-label="افزایش تعداد"
                      :disabled="busyItem === item.id || item.quantity >= item.product.stock"
                      @click="changeItem(item.id, item.quantity + 1)"
                    >
                      +
                    </button>
                  </div>
                </div>
              </li>
            </ul>

            <div class="p-4 border-t border-base-200 space-y-3">
              <p v-if="itemError" class="rounded-xl bg-error/10 px-3 py-2 text-sm font-bold text-error">
                {{ itemError }}
              </p>
              <div class="flex justify-between font-bold">
                <span>جمع کل</span>
                <span class="text-primary">{{ formatPrice(cart.total) }}</span>
              </div>
              <NuxtLink to="/shop" class="btn btn-outline w-full rounded-full" @click="cart.closeDrawer()">
                ادامه خرید
              </NuxtLink>
              <NuxtLink to="/checkout" class="btn btn-primary w-full rounded-full" @click="cart.closeDrawer()">
                تسویه حساب
              </NuxtLink>
            </div>
          </template>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { useCartStore } from '~/stores/cart'

const cart = useCartStore()
const { formatPrice, extractApiError } = useApi()
const { normalizeMediaUrl } = useMediaUrl()

const busyItem = ref<string | null>(null)
const itemError = ref('')

/** Quantity 0 removes the line. Errors (stock ran out) were unhandled rejections before. */
async function changeItem(itemId: string, quantity: number) {
  busyItem.value = itemId
  itemError.value = ''
  try {
    if (quantity <= 0) await cart.removeItem(itemId)
    else await cart.updateItem(itemId, quantity)
  } catch (error) {
    itemError.value = extractApiError(error, 'به‌روزرسانی سبد خرید انجام نشد')
  } finally {
    busyItem.value = null
  }
}

watch(() => cart.drawerOpen, (isOpen) => {
  if (isOpen) itemError.value = ''
  document.body.style.overflow = isOpen ? 'hidden' : ''
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-slide-in-ltr {
  animation: slideInLtr 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideInLtr {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
</style>
