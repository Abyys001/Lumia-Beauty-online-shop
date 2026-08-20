<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div class="text-6xl mb-4">❌</div>
    <h1 class="text-2xl font-bold text-error mb-2">پرداخت ناموفق</h1>
    <p class="text-base-content/70">{{ decodedMessage }}</p>
    <p v-if="orderNumber" class="text-sm text-base-content/50 mt-2">شماره سفارش: {{ orderNumber }}</p>
    <div class="flex gap-3 justify-center mt-8">
      <NuxtLink
        v-if="orderNumber"
        :to="`/checkout/pending?order=${orderNumber}`"
        class="btn-lumia"
      >
        راهنمای پرداخت همین سفارش
      </NuxtLink>
      <NuxtLink to="/checkout" class="btn btn-outline rounded-full">سفارش جدید</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

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

useSeoMeta({
  title: 'پرداخت ناموفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
