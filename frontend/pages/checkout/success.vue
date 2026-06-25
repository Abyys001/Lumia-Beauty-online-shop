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
      <p v-if="refId" class="text-sm text-base-content/50">کد پیگیری: {{ refId }}</p>
      <p v-if="verifyError" class="text-sm text-warning mt-2">{{ verifyError }}</p>
      <div class="flex gap-3 justify-center mt-8">
        <NuxtLink to="/account" class="btn-lumia">مشاهده سفارشات</NuxtLink>
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
const verifying = ref(true)
const verifyError = ref('')

onMounted(async () => {
  await cart.fetchCart()
  if (!orderNumber.value || !auth.isAuthenticated) {
    verifying.value = false
    return
  }
  try {
    const order = await apiFetch<Order>(`/orders/${orderNumber.value}/`)
    if (order.status !== 'paid') {
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
