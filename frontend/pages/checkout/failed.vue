<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div class="text-6xl mb-4">❌</div>
    <h1 class="text-2xl font-bold text-error mb-2">پرداخت ناموفق</h1>
    <p class="text-base-content/70">{{ decodedMessage }}</p>
    <p v-if="orderNumber" class="text-sm text-base-content/50 mt-2">شماره سفارش: {{ orderNumber }}</p>
    <div class="flex gap-3 justify-center mt-8">
      <button
        v-if="orderNumber"
        class="btn-lumia"
        :disabled="retrying"
        @click="retryPayment"
      >
        <span v-if="retrying" class="loading loading-spinner loading-sm" />
        <span v-else>پرداخت مجدد همین سفارش</span>
      </button>
      <NuxtLink to="/checkout" class="btn btn-outline rounded-full">سفارش جدید</NuxtLink>
    </div>
    <p v-if="retryError" class="text-error text-sm mt-3">{{ retryError }}</p>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { apiFetch } = useApi()

const orderNumber = computed(() => route.query.order as string)
const decodedMessage = computed(() => {
  const raw = route.query.message as string
  if (!raw) return 'متأسفانه پرداخت انجام نشد. لطفاً دوباره تلاش کنید.'
  try {
    return decodeURIComponent(raw)
  } catch {
    return raw
  }
})

const retrying = ref(false)
const retryError = ref('')

async function retryPayment() {
  if (!orderNumber.value) return
  retrying.value = true
  retryError.value = ''
  try {
    const payment = await apiFetch<{ redirect_url: string }>('/payments/zarinpal/request/', {
      method: 'POST',
      body: { order_number: orderNumber.value },
    })
    window.location.href = payment.redirect_url
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    retryError.value = err.data?.detail || 'خطا در اتصال به درگاه'
    retrying.value = false
  }
}

useSeoMeta({
  title: 'پرداخت ناموفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
