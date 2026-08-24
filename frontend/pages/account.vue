<template>
  <div v-if="!auth.isAuthenticated" class="container-lumia py-6 sm:py-8">
    <div class="max-w-md mx-auto">
      <AccountEmptyState
        icon="🔒"
        title="ورود به حساب کاربری"
        description="برای مشاهده سفارشات، آدرس‌ها و پروفایل خود وارد شوید."
        action-label="ورود / ثبت‌نام"
        to="/auth"
      />
    </div>
  </div>
  <NuxtPage v-else />
</template>

<script setup lang="ts">
const auth = useAuthStore()

useSeoMeta({ robots: 'noindex, nofollow' })
</script>
