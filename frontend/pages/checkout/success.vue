<template>
  <div class="container-lumia py-8 max-w-3xl">
    <div v-if="verifying" class="py-16 text-center">
      <span class="loading loading-spinner loading-lg text-success" />
      <p class="mt-4 text-base-content/70">در حال بارگذاری سفارش...</p>
    </div>

    <template v-else-if="order">
      <CheckoutPaymentInstructions
        v-if="order.status === 'pending'"
        :purchase-code="order.purchase_code || ''"
        :total="order.total"
        :expires-at="order.expires_at"
      />

      <div v-else class="rounded-3xl border-2 border-success/30 bg-success/5 p-8 text-center">
        <div class="text-6xl mb-4">✅</div>
        <h1 class="text-2xl font-black text-success mb-2">سفارش شما ثبت و پرداخت شد</h1>
        <p class="text-base-content/70">
          شماره سفارش: <strong class="font-mono" dir="ltr">{{ order.order_number }}</strong>
        </p>
      </div>

      <div class="flex flex-wrap gap-3 justify-center mt-8">
        <NuxtLink :to="`/account/orders/${order.order_number}`" class="btn-lumia">پیگیری سفارش</NuxtLink>
        <NuxtLink to="/shop" class="btn btn-outline rounded-full">ادامه خرید</NuxtLink>
      </div>
    </template>

    <div v-else class="rounded-3xl border-2 border-dashed border-base-300 p-12 text-center">
      <div class="mb-3 text-5xl">🔍</div>
      <p class="font-bold text-lumia-dark">سفارشی پیدا نشد</p>
      <p class="mt-1 text-sm text-base-content/60">
        اگر همین حالا خرید کرده‌اید، سفارش را از حساب کاربری خود دنبال کنید.
      </p>
      <NuxtLink to="/account?tab=orders" class="btn btn-primary rounded-full mt-5">سفارش‌های من</NuxtLink>
    </div>
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

onMounted(async () => {
  await cart.fetchCart().catch(() => {})
  if (!orderNumber.value || !auth.isAuthenticated) {
    verifying.value = false
    return
  }
  try {
    order.value = await apiFetch<Order>(`/orders/${orderNumber.value}/`)
  } catch {
    order.value = null
  } finally {
    verifying.value = false
  }
})

useSeoMeta({
  title: 'ثبت سفارش موفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
