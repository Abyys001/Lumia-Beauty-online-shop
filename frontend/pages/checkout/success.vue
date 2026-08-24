<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div v-if="verifying" class="py-8">
      <span class="loading loading-spinner loading-lg text-success" />
      <p class="mt-4 text-base-content/70">در حال بارگذاری سفارش...</p>
    </div>
    <template v-else>
      <div class="text-6xl mb-4">✅</div>
      <h1 class="text-2xl font-bold text-success mb-2">سفارش شما ثبت شد</h1>
      <p class="text-base-content/70 mb-4">لطفاً کد خرید زیر را برای پیگیری و تأیید پرداخت ارسال کنید.</p>

      <p v-if="orderNumber" class="text-sm mb-4">شماره سفارش: <strong>{{ orderNumber }}</strong></p>

      <div v-if="order?.purchase_code" class="inline-flex flex-col items-center gap-2 rounded-2xl border border-lumia-gold/30 bg-lumia-gold/5 px-6 py-4">
        <span class="text-xs text-base-content/60">کد خرید شما:</span>
        <span class="font-mono text-3xl font-bold tracking-widest text-lumia-gold" dir="ltr">{{ order.purchase_code }}</span>
        <button class="btn btn-outline btn-xs rounded-full border-lumia-gold/40 text-lumia-gold" @click="copyPurchaseCode">
          کپی کد
        </button>
      </div>

      <div class="mt-6 bg-base-200/50 rounded-2xl p-4 text-right">
        <p class="text-sm font-bold mb-2">مراحل بعدی:</p>
        <ol class="text-sm text-base-content/70 space-y-1 list-decimal list-inside">
          <li>کد خرید بالا را کپی کنید</li>
          <li>از طریق یکی از راه‌های زیر برای ما ارسال کنید</li>
          <li>پس از تأیید پرداخت، سفارش شما ارسال خواهد شد</li>
        </ol>
      </div>

      <div class="mt-4 flex flex-wrap gap-2 justify-center">
        <a :href="`https://wa.me/${adminPhone}`" target="_blank" class="btn btn-sm btn-outline rounded-full">
          <i class="fab fa-whatsapp ml-1"></i> واتساپ
        </a>
        <a :href="`https://t.me/${adminTelegram}`" target="_blank" class="btn btn-sm btn-outline rounded-full">
          <i class="fab fa-telegram ml-1"></i> تلگرام
        </a>
        <a :href="`sms:${adminPhone}`" class="btn btn-sm btn-outline rounded-full">
          پیامک
        </a>
      </div>

      <p v-if="order?.status === 'pending'" class="text-xs text-warning mt-4">
        سفارش شما در انتظار تأیید پرداخت است.
      </p>

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
const order = ref<Order | null>(null)
const verifying = ref(true)

const adminPhone = '09120000000'
const adminTelegram = 'lumiabeauty'

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
  } catch {
    // order not found
  } finally {
    verifying.value = false
  }
})

useSeoMeta({
  title: 'ثبت سفارش موفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
