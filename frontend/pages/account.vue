<template>
  <!-- Auth state only exists after the client plugin hydrates it, so SSR must not
       guess which branch to render — it always mismatched for signed-in visitors. -->
  <ClientOnly>
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

    <template #fallback>
      <div class="container-lumia flex justify-center py-20">
        <span class="loading loading-spinner loading-lg text-primary" />
      </div>
    </template>
  </ClientOnly>
</template>

<script setup lang="ts">
const auth = useAuthStore()

useSeoMeta({ robots: 'noindex, nofollow' })
</script>
