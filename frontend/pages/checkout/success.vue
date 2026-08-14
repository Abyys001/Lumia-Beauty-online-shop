<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div v-if="verifying" class="py-8">
      <span class="loading loading-spinner loading-lg text-success" />
      <p class="mt-4 text-base-content/70">در حال تأیید پرداخت...</p>
    </div>
    <template v-else>
      <div class="text-6xl mb-4">✅</div>
      <h1 class="text-2xl font-bold text-success mb-2">پرداخت موفق</h1>
      <p class="text-base-content/70 mb-2">سفارش شما با موفقیت ثبت شد.</p>
      <p v-if="orderNumber" class="text-sm">شماره سفارش: <strong>{{ orderNumber }}</strong></p>
      <div v-if="order?.purchase_code" class="mt-4 inline-flex flex-col items-center gap-2 rounded-2xl border border-lumia-gold/30 bg-lumia-gold/5 px-6 py-4">
        <span class="text-xs text-base-content/60">کد خرید (برای پیگیری سفارش):</span>
        <span class="font-mono text-2xl font-bold tracking-widest text-lumia-gold" dir="ltr">{{ order.purchase_code }}</span>
        <button class="btn btn-outline btn-xs rounded-full border-lumia-gold/40 text-lumia-gold" @click="copyPurchaseCode">
          کپی کد
        </button>
      </div>
      <p v-if="refId" class="text-sm text-base-content/50 mt-3">کد پیگیری: {{ refId }}</p>
      <p v-if="verifyError" class="text-sm text-warning mt-2">{{ verifyError }}</p>
      <div class="flex gap-3 justify-center mt-8">
        <NuxtLink to="/account?tab=orders" class="btn-lumia">مشاهده سفارشات</NuxtLink>
        <NuxtLink to="/shop" class="btn btn-outline rounded-full">ادامه خرید</NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Order } from '~/types'
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()
const { apiFetch } = useApi()

const orderNumber = computed(() => route.query.order as string)
const refId = computed(() => route.query.ref as string)
const order = ref<Order | null>(null)
const verifying = ref(true)
const verifyError = ref('')

async function copyPurchaseCode() {
  if (!order.value?.purchase_code || !import.meta.client) return
  await navigator.clipboard.writeText(order.value.purchase_code)
}

onMounted(async () => {
  await cart.fetchCart()
  if (!orderNumber.value || !auth.isAuthenticated) {
    verifying.value = false
    return
  }
  try {
    order.value = await apiFetch<Order>(`/orders/${orderNumber.value}/`)
    if (order.value.status !== 'paid') {
      verifyError.value = 'وضعیت سفارش هنوز «پرداخت شده» نیست — در صورت کسر مبلغ با پشتیبانی تماس بگیرید.'
    }
  } catch {
    verifyError.value = 'امکان تأیید وضعیت سفارش از سرور وجود ندارد.'
  } finally {
    verifying.value = false
  }
})

useSeoMeta({
  title: 'پرداخت موفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
