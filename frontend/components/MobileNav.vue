<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[70] lg:hidden"
        @keydown.escape="closeNav"
      >
        <div class="absolute inset-0 bg-lumia-dark/40 backdrop-blur-xs" @click="closeNav" />

        <div
          class="absolute top-0 bottom-0 right-0 w-full max-w-xs sm:max-w-sm bg-base-100 shadow-2xl flex flex-col animate-slide-in-rtl"
          role="dialog"
          aria-label="منوی موبایل"
        >
          <div class="flex items-center justify-between p-4 border-b border-base-200">
            <span class="font-bold text-lg text-lumia-dark">منو</span>
            <button class="btn btn-ghost btn-sm btn-circle" aria-label="بستن منو" @click="closeNav">✕</button>
          </div>

          <nav class="flex-1 overflow-y-auto p-4 space-y-1">
            <NuxtLink to="/" class="nav-link" @click="closeNav">خانه</NuxtLink>
            <NuxtLink to="/shop" class="nav-link" @click="closeNav">فروشگاه</NuxtLink>
            <NuxtLink to="/blog" class="nav-link" @click="closeNav">وبلاگ</NuxtLink>
            <NuxtLink to="/about" class="nav-link" @click="closeNav">درباره ما</NuxtLink>
            <NuxtLink to="/contact" class="nav-link" @click="closeNav">تماس با ما</NuxtLink>
            <NuxtLink to="/account" class="nav-link" @click="closeNav">حساب کاربری</NuxtLink>
          </nav>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const { open, closeNav } = useMobileNav()
const route = useRoute()

watch(() => route.path, closeNav)
watch(open, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})
</script>

<style scoped>
.nav-link {
  @apply block px-3 py-2.5 rounded-xl text-sm font-medium text-base-content hover:bg-base-200 hover:text-primary transition-colors;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-slide-in-rtl {
  animation: slideInRtl 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideInRtl {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
