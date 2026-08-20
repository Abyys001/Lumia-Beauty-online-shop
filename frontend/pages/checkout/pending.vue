<template>
  <div class="container-lumia py-8 max-w-5xl">
    <div v-if="pending" class="flex justify-center py-24">
      <span class="loading loading-spinner loading-lg text-primary" />
    </div>

    <div v-else-if="order" class="grid lg:grid-cols-3 gap-6">
      <!-- Instructions -->
      <div class="lg:col-span-2">
        <CheckoutPaymentInstructions
          :purchase-code="order.purchase_code || ''"
          :total="order.total"
          :expires-at="order.expires_at"
        />
      </div>

      <!-- Invoice summary -->
      <div class="space-y-4">
        <div class="sticky top-4 space-y-4">
          <div class="rounded-3xl border-2 border-base-200 bg-white p-5 shadow-sm text-right">
            <h2 class="mb-4 flex items-center justify-between font-black text-lumia-dark">
              <span>فاکتور سفارش</span>
              <span class="font-mono text-xs text-lumia-dark/40" dir="ltr">{{ order.order_number }}</span>
            </h2>

            <div class="max-h-56 space-y-2 overflow-y-auto pl-1">
              <div
                v-for="item in order.items"
                :key="item.id"
                class="flex items-start justify-between gap-2 border-b border-base-200 pb-2 text-sm"
              >
                <span class="flex-1 leading-6">{{ item.product_name }}</span>
                <span class="shrink-0 text-xs text-lumia-dark/50">× {{ item.quantity }}</span>
                <span class="shrink-0 font-bold">{{ formatPrice(item.subtotal) }}</span>
              </div>
            </div>

            <div class="mt-4 space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-lumia-dark/60">جمع اقلام</span>
                <span>{{ formatPrice(order.subtotal) }}</span>
              </div>
              <div v-if="order.discount_amount" class="flex justify-between text-success">
                <span>تخفیف</span>
                <span>− {{ formatPrice(order.discount_amount) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-lumia-dark/60">هزینه ارسال</span>
                <span>{{ formatPrice(order.shipping_cost) }}</span>
              </div>
              <div class="flex justify-between border-t-2 border-lumia-gold/30 pt-3 text-lg font-black">
                <span>مبلغ قابل واریز</span>
                <span class="text-lumia-gold">{{ formatPrice(order.total) }}</span>
              </div>
              <p class="text-left text-xs text-lumia-dark/40">تومان</p>
            </div>
          </div>

          <!-- Shipping recap -->
          <div class="rounded-3xl border border-base-200 bg-white p-5 shadow-sm text-right text-sm">
            <h3 class="mb-2 font-bold text-lumia-dark">اطلاعات ارسال</h3>
            <p>{{ order.shipping_name }} — <span dir="ltr">{{ order.shipping_phone }}</span></p>
            <p class="mt-1 text-lumia-dark/70 leading-6">
              {{ order.shipping_province }}، {{ order.shipping_city }} — {{ order.shipping_address }}
            </p>
            <p v-if="order.shipping_plate_number" class="mt-1 text-lumia-dark/50">پلاک/واحد: {{ order.shipping_plate_number }}</p>
            <p v-if="order.shipping_postal_code" class="mt-1 text-lumia-dark/50">کد پستی: {{ order.shipping_postal_code }}</p>
          </div>

          <div class="flex flex-col gap-2">
            <NuxtLink :to="`/account/orders/${order.order_number}`" class="btn btn-outline rounded-full w-full">
              پیگیری وضعیت سفارش
            </NuxtLink>
            <NuxtLink to="/shop" class="btn btn-ghost rounded-full w-full">ادامه خرید</NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="py-24 text-center">
      <div class="mb-4 text-6xl">🔍</div>
      <h1 class="mb-2 text-2xl font-bold text-lumia-dark">سفارش یافت نشد</h1>
      <p class="text-base-content/60">این سفارش وجود ندارد یا به حساب شما تعلق ندارد.</p>
      <NuxtLink to="/account?tab=orders" class="btn-lumia mt-6">سفارشات من</NuxtLink>
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
const { apiFetch, formatPrice } = useApi()

const orderNumber = computed(() => route.query.order as string)
const order = ref<Order | null>(null)
const pending = ref(true)

onMounted(async () => {
  // The order now owns the items — refresh so the header count drops to zero.
  cart.fetchCart().catch(() => {})

  if (!orderNumber.value || !auth.isAuthenticated) {
    pending.value = false
    return
  }
  try {
    order.value = await apiFetch<Order>(`/orders/${orderNumber.value}/`)
  } catch {
    order.value = null
  } finally {
    pending.value = false
  }
})

useSeoMeta({
  title: 'پرداخت سفارش | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
