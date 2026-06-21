<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div class="text-6xl mb-4">✅</div>
    <h1 class="text-2xl font-bold text-success mb-2">پرداخت موفق</h1>
    <p class="text-base-content/70 mb-2">سفارش شما با موفقیت ثبت شد.</p>
    <p v-if="orderNumber" class="text-sm">شماره سفارش: <strong>{{ orderNumber }}</strong></p>
    <p v-if="refId" class="text-sm text-base-content/50">کد پیگیری: {{ refId }}</p>
    <div class="flex gap-3 justify-center mt-8">
      <NuxtLink to="/account" class="btn-lumia">مشاهده سفارشات</NuxtLink>
      <NuxtLink to="/shop" class="btn btn-outline rounded-full">ادامه خرید</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const orderNumber = computed(() => route.query.order as string)
const refId = computed(() => route.query.ref as string)

useSeoMeta({
  title: 'پرداخت موفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
