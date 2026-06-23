<template>
  <ClientOnly>
    <div v-if="auth.user?.is_staff" class="sticky top-0 z-[60] bg-neutral text-neutral-content">
      <div class="container-lumia flex items-center justify-between py-1.5 text-sm">
        <span class="opacity-70">پنل مدیریت</span>
        <NuxtLink to="/admin" class="inline-flex items-center gap-1.5 font-semibold hover:opacity-80 transition-opacity">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          ورود به مدیریت
        </NuxtLink>
      </div>
    </div>
  </ClientOnly>
  <header class="sticky top-0 z-50 bg-base-100/95 backdrop-blur-md border-b border-base-200">
    <div class="container-lumia">
      <div class="navbar min-h-16 px-0">
        <div class="navbar-start">
          <button
            type="button"
            class="btn btn-ghost btn-circle lg:hidden"
            aria-label="باز کردن منو"
            @click="openNav"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <NuxtLink to="/" class="flex items-center gap-2.5 text-xl font-bold text-primary tracking-wide">
            <img src="/logo.svg" alt="Lumia Beauty Logo" class="w-8 h-8 object-contain" />
            <span>Lumia Beauty</span>
          </NuxtLink>
        </div>

        <div class="navbar-center hidden lg:flex">
          <ul class="menu menu-horizontal px-1 gap-1 items-center">
            <li><NuxtLink to="/" class="rounded-full">خانه</NuxtLink></li>
            <li><NuxtLink to="/shop" class="rounded-full">فروشگاه</NuxtLink></li>
            <li><NuxtLink to="/blog" class="rounded-full">وبلاگ</NuxtLink></li>
            <li><NuxtLink to="/about" class="rounded-full">درباره ما</NuxtLink></li>
            <li><NuxtLink to="/contact" class="rounded-full">تماس با ما</NuxtLink></li>
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
              class="badge badge-primary badge-sm absolute -top-1 -end-1"
            >
              {{ cart.itemCount }}
            </span>
          </button>
          <ClientOnly>
            <NuxtLink
              :to="auth.user?.is_staff ? '/admin' : (auth.isAuthenticated ? '/account' : '/auth')"
              class="btn btn-ghost btn-circle"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </NuxtLink>
            <template #fallback>
              <NuxtLink to="/auth" class="btn btn-ghost btn-circle">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </NuxtLink>
            </template>
          </ClientOnly>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

const cart = useCartStore()
const auth = useAuthStore()
const { openNav } = useMobileNav()
</script>
