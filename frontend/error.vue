<template>
  <div data-theme="lumia" class="min-h-screen flex items-center justify-center bg-lumia-light/50 px-4">
    <div class="max-w-md w-full text-center space-y-6 p-8 bg-white rounded-3xl border border-lumia-cream shadow-sm">
      <span class="text-5xl">⚠️</span>
      <h1 class="text-2xl font-bold text-lumia-dark">مشکلی پیش آمد</h1>
      <p class="text-sm text-base-content/60 leading-relaxed">
        {{ error?.message || 'در بارگذاری این صفحه خطایی رخ داد. لطفاً دوباره تلاش کنید.' }}
      </p>
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <button class="btn btn-primary rounded-full" @click="handleError">تلاش مجدد</button>
        <NuxtLink to="/" class="btn btn-outline rounded-full">بازگشت به خانه</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  error: { message?: string; statusCode?: number }
}>()

function handleError() {
  clearError({ redirect: '/' })
}
</script>
