<template>
  <header class="sticky top-0 z-50 bg-base-100/95 backdrop-blur-md border-b border-base-200">
    <div class="container-lumia">
      <div class="navbar min-h-16 px-0">
        <div class="navbar-start">
          <label for="mobile-drawer" class="btn btn-ghost btn-circle lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </label>
          <NuxtLink to="/" class="flex items-center gap-2.5 text-xl font-bold text-primary tracking-wide">
            <img src="/logo.svg" alt="Lumia Beauty Logo" class="w-8 h-8 object-contain" />
            <span>Lumia Beauty</span>
          </NuxtLink>
        </div>

        <div class="navbar-center hidden lg:flex">
          <ul class="menu menu-horizontal px-1 gap-1">
            <li><NuxtLink to="/" class="rounded-full">خانه</NuxtLink></li>
            <li><NuxtLink to="/shop" class="rounded-full">فروشگاه</NuxtLink></li>
            <li><NuxtLink to="/blog" class="rounded-full">وبلاگ</NuxtLink></li>
            <li><NuxtLink to="/about" class="rounded-full">درباره ما</NuxtLink></li>
          </ul>
        </div>

        <div class="navbar-end gap-2">
          <LiveSearch />
          <button class="btn btn-ghost btn-circle relative" @click="cart.openDrawer()">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
            </svg>
            <span
              v-if="cart.itemCount > 0"
              class="badge badge-primary badge-sm absolute -top-1 -left-1"
            >
              {{ cart.itemCount }}
            </span>
          </button>
          <NuxtLink
            :to="auth.isAuthenticated ? '/account' : '/auth'"
            class="btn btn-ghost btn-circle"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </NuxtLink>
        </div>
      </div>
    </div>

    <div class="drawer drawer-end lg:hidden">
      <input id="mobile-drawer" type="checkbox" class="drawer-toggle" />
      <div class="drawer-side z-50">
        <label for="mobile-drawer" class="drawer-overlay" />
        <ul class="menu p-4 w-64 min-h-full bg-base-100 text-base-content">
          <li class="menu-title">منو</li>
          <li><NuxtLink to="/">خانه</NuxtLink></li>
          <li><NuxtLink to="/shop">فروشگاه</NuxtLink></li>
          <li><NuxtLink to="/blog">وبلاگ</NuxtLink></li>
          <li><NuxtLink to="/about">درباره ما</NuxtLink></li>
          <li><NuxtLink to="/account">حساب کاربری</NuxtLink></li>
        </ul>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const cart = useCartStore()
const auth = useAuthStore()
</script>
