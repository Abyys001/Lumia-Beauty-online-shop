<template>
  <div class="max-w-4xl space-y-6">
    <p class="text-sm text-lumia-dark/60">
      تنظیمات سیستم، درگاه پرداخت و پیامک را از این بخش مدیریت کنید.
    </p>

    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <NuxtLink
        to="/admin/settings/payment"
        class="bg-white rounded-2xl p-5 border border-base-200 shadow-sm hover:border-lumia-gold/50 hover:shadow-md transition-all group"
      >
        <div class="w-10 h-10 rounded-xl bg-lumia-gold/15 flex items-center justify-center mb-3 group-hover:bg-lumia-gold/25">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-lumia-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
          </svg>
        </div>
        <h2 class="font-bold text-lumia-dark mb-1">درگاه پرداخت</h2>
        <p class="text-xs text-lumia-dark/50">Zarinpal Merchant ID و تنظیمات پرداخت</p>
      </NuxtLink>

      <NuxtLink
        to="/admin/settings/sms"
        class="bg-white rounded-2xl p-5 border border-base-200 shadow-sm hover:border-lumia-gold/50 hover:shadow-md transition-all group"
      >
        <div class="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h2 class="font-bold text-lumia-dark mb-1">SMS و OTP</h2>
        <p class="text-xs text-lumia-dark/50">SMS.ir، قالب OTP، محدودیت‌ها و JWT</p>
      </NuxtLink>

      <NuxtLink
        to="/admin/sms/logs"
        class="bg-white rounded-2xl p-5 border border-base-200 shadow-sm hover:border-lumia-gold/50 hover:shadow-md transition-all group"
      >
        <div class="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 class="font-bold text-lumia-dark mb-1">لاگ پیامک</h2>
        <p class="text-xs text-lumia-dark/50">تاریخچه ارسال، خطاها و پاسخ provider</p>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })
</script>
