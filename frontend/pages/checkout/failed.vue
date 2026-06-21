<template>
  <div class="container-lumia py-16 text-center max-w-lg mx-auto">
    <div class="text-6xl mb-4">❌</div>
    <h1 class="text-2xl font-bold text-error mb-2">پرداخت ناموفق</h1>
    <p class="text-base-content/70">{{ message || 'متأسفانه پرداخت انجام نشد. لطفاً دوباره تلاش کنید.' }}</p>
    <div class="flex gap-3 justify-center mt-8">
      <NuxtLink to="/checkout" class="btn-lumia">تلاش مجدد</NuxtLink>
      <NuxtLink to="/cart" class="btn btn-outline rounded-full">بازگشت به سبد</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const message = computed(() => route.query.message as string)

useSeoMeta({
  title: 'پرداخت ناموفق | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
