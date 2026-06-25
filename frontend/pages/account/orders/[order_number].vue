<template>
  <div class="container-lumia py-8 max-w-3xl">
    <div v-if="pending" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg" />
    </div>

    <div v-else-if="order" class="space-y-6">
      <div class="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 class="section-title">سفارش {{ order.order_number }}</h1>
          <p class="text-sm text-base-content/60">{{ formatDate(order.created_at) }}</p>
        </div>
        <span class="badge badge-lg" :class="statusBadge(order.status)">{{ order.status_display }}</span>
      </div>

      <!-- Status timeline -->
      <div class="card-lumia p-6">
        <h2 class="font-bold mb-4">وضعیت سفارش</h2>
        <ul class="steps steps-vertical lg:steps-horizontal w-full">
          <li
            v-for="step in timelineSteps"
            :key="step.key"
            class="step"
            :class="{ 'step-primary': step.done, 'step-neutral': !step.done }"
            :data-content="step.done ? '✓' : ''"
          >
            <span class="text-xs sm:text-sm">{{ step.label }}</span>
          </li>
        </ul>
      </div>

      <!-- Tracking -->
      <div v-if="order.tracking_number" class="card-lumia p-6 bg-info/5 border-info/20">
        <h2 class="font-bold mb-2">کد رهگیری پست</h2>
        <p class="font-mono text-lg tracking-wider mb-3" dir="ltr">{{ order.tracking_number }}</p>
        <div class="flex flex-wrap gap-2">
          <button class="btn btn-outline btn-sm rounded-full" @click="copyTracking">کپی کد</button>
          <a
            :href="`https://tracking.post.ir/?id=${order.tracking_number}`"
            target="_blank"
            rel="noopener"
            class="btn btn-primary btn-sm rounded-full"
          >
            پیگیری در سایت پست
          </a>
        </div>
      </div>

      <!-- Items -->
      <div class="card-lumia p-6">
        <h2 class="font-bold mb-4">اقلام سفارش</h2>
        <div class="space-y-3">
          <div v-for="item in order.items" :key="item.id" class="flex justify-between text-sm border-b border-base-200 pb-2">
            <span>{{ item.product_name }} × {{ item.quantity }}</span>
            <span class="font-bold">{{ formatPrice(item.subtotal) }}</span>
          </div>
        </div>
        <div class="mt-4 space-y-1 text-sm">
          <div class="flex justify-between"><span class="text-base-content/60">جمع جزء</span><span>{{ formatPrice(order.subtotal) }}</span></div>
          <div v-if="order.discount_amount" class="flex justify-between text-success"><span>تخفیف</span><span>− {{ formatPrice(order.discount_amount) }}</span></div>
          <div class="flex justify-between"><span class="text-base-content/60">ارسال</span><span>{{ order.shipping_cost ? formatPrice(order.shipping_cost) : 'رایگان' }}</span></div>
          <div class="flex justify-between font-bold text-lg pt-2"><span>مبلغ نهایی</span><span class="text-primary">{{ formatPrice(order.total) }}</span></div>
        </div>
        <button
          v-if="order.status === 'pending'"
          class="btn btn-primary rounded-full w-full mt-4"
          :disabled="paying"
          @click="payOrder"
        >
          <span v-if="paying" class="loading loading-spinner loading-sm" />
          <span v-else>پرداخت سفارش</span>
        </button>
        <p v-if="payError" class="text-error text-sm mt-2 text-center">{{ payError }}</p>
        <button
          v-if="canReorder"
          class="btn btn-outline btn-primary rounded-full w-full mt-4"
          :disabled="reordering"
          @click="reorder"
        >
          <span v-if="reordering" class="loading loading-spinner loading-sm" />
          <span v-else>خرید مجدد</span>
        </button>
      </div>

      <!-- Shipping -->
      <div class="card-lumia p-6">
        <h2 class="font-bold mb-3">آدرس ارسال</h2>
        <p class="text-sm">{{ order.shipping_name }} — {{ order.shipping_phone }}</p>
        <p class="text-sm text-base-content/70 mt-1">
          {{ order.shipping_province }}، {{ order.shipping_city }} — {{ order.shipping_address }}
        </p>
        <p v-if="order.shipping_postal_code" class="text-sm text-base-content/50 mt-1">کد پستی: {{ order.shipping_postal_code }}</p>
        <p v-if="order.coupon_code" class="text-sm mt-3">کد تخفیف: <span class="font-mono">{{ order.coupon_code }}</span></p>
        <p v-if="order.note" class="text-sm mt-2 text-base-content/60">یادداشت: {{ order.note }}</p>
      </div>
    </div>

    <div v-else class="text-center py-16 text-base-content/50">سفارش یافت نشد</div>
  </div>
</template>

<script setup lang="ts">
import type { Order } from '~/types'
import { useCartStore } from '~/stores/cart'

const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()
const { apiFetch, formatPrice, formatDate } = useApi()

const orderNumber = computed(() => route.params.order_number as string)
const reordering = ref(false)
const paying = ref(false)
const payError = ref('')

const { data: order, pending } = await useAsyncData(
  () => `order-${orderNumber.value}`,
  () => auth.isAuthenticated
    ? apiFetch<Order>(`/orders/${orderNumber.value}/`)
    : Promise.resolve(null as Order | null),
)

const STATUS_FLOW = ['pending', 'paid', 'processing', 'shipped', 'delivered'] as const
const STATUS_LABELS: Record<string, string> = {
  pending: 'ثبت سفارش',
  paid: 'پرداخت شده',
  processing: 'در حال پردازش',
  shipped: 'ارسال شده',
  delivered: 'تحویل داده شده',
  cancelled: 'لغو شده',
  refunded: 'مرجوع شده',
}

const timelineSteps = computed(() => {
  if (!order.value) return []
  const current = order.value.status
  if (current === 'cancelled' || current === 'refunded') {
    return [{ key: current, label: STATUS_LABELS[current], done: true }]
  }
  const idx = STATUS_FLOW.indexOf(current as typeof STATUS_FLOW[number])
  return STATUS_FLOW.map((key, i) => ({
    key,
    label: STATUS_LABELS[key],
    done: idx >= 0 ? i <= idx : key === 'pending',
  }))
})

const canReorder = computed(() =>
  order.value && !['cancelled', 'refunded', 'pending'].includes(order.value.status),
)

function statusBadge(status: string) {
  const map: Record<string, string> = {
    paid: 'badge-success',
    pending: 'badge-warning',
    processing: 'badge-info',
    shipped: 'badge-info',
    delivered: 'badge-success',
    cancelled: 'badge-error',
    refunded: 'badge-error',
  }
  return map[status] || 'badge-ghost'
}

async function copyTracking() {
  if (!order.value?.tracking_number || !import.meta.client) return
  await navigator.clipboard.writeText(order.value.tracking_number)
}

async function payOrder() {
  if (!order.value) return
  paying.value = true
  payError.value = ''
  try {
    const payment = await apiFetch<{ redirect_url: string }>('/payments/zarinpal/request/', {
      method: 'POST',
      body: { order_number: order.value.order_number },
    })
    window.location.href = payment.redirect_url
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    payError.value = err.data?.detail || 'خطا در اتصال به درگاه'
    paying.value = false
  }
}

async function reorder() {
  if (!order.value) return
  reordering.value = true
  try {
    for (const item of order.value.items) {
      if (item.product) {
        await cart.addItem(item.product, item.quantity)
      }
    }
    await navigateTo('/checkout')
  } catch {
    alert('برخی محصولات موجود نیستند یا به سبد اضافه نشدند')
  } finally {
    reordering.value = false
  }
}

useSeoMeta({
  title: () => order.value ? `سفارش ${order.value.order_number} | لومیا بیوتی` : 'جزئیات سفارش',
  robots: 'noindex, nofollow',
})
</script>
