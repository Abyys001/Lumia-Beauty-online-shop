<template>
  <div data-theme="lumia" class="min-h-screen flex" dir="rtl">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'w-64 min-h-screen bg-lumia-dark text-lumia-light flex flex-col fixed top-0 right-0 z-40 transition-transform duration-300',
        sidebarOpen ? 'translate-x-0' : 'translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Logo -->
      <div class="px-6 py-5 border-b border-white/10">
        <NuxtLink to="/admin" class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-lumia-gold flex items-center justify-center text-lumia-dark font-bold text-lg">L</div>
          <div>
            <div class="text-lumia-gold font-bold text-sm">لومیا بیوتی</div>
            <div class="text-white/40 text-xs">پنل مدیریت</div>
          </div>
        </NuxtLink>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 overflow-y-auto">
        <div class="px-3 mb-2 text-white/30 text-xs font-medium tracking-wider px-4">فروشگاه</div>
        <AdminNavItem to="/admin" icon="dashboard" label="داشبورد" :exact="true" />
        <AdminNavItem to="/admin/products" icon="products" label="محصولات" />
        <AdminNavItem to="/admin/categories" icon="categories" label="دسته‌بندی‌ها" />
        <AdminNavItem to="/admin/brands" icon="brands" label="برندها" />
        <AdminNavItem to="/admin/orders" icon="orders" label="سفارشات" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">مدیریت</div>
        <AdminNavItem to="/admin/users" icon="users" label="کاربران" />
        <AdminNavItem to="/admin/coupons" icon="coupons" label="کدهای تخفیف" />
        <AdminNavItem to="/admin/reviews" icon="reviews" label="نظرات" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">محتوا</div>
        <AdminNavItem to="/admin/blog" icon="blog" label="وبلاگ" />
        <AdminNavItem to="/admin/instagram" icon="instagram" label="اینستاگرام" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">سیستم</div>
        <AdminNavItem to="/admin/settings" icon="settings" label="تنظیمات" :exact="true" />
        <AdminNavItem to="/admin/settings/sms" icon="sms" label="SMS و OTP" />
        <AdminNavItem to="/admin/sms/logs" icon="logs" label="لاگ پیامک" />
      </nav>

      <!-- User -->
      <div class="px-4 py-4 border-t border-white/10">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-lumia-gold/20 flex items-center justify-center text-lumia-gold text-sm font-bold">
            {{ auth.user?.phone?.slice(-4) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-white/80 text-xs truncate">{{ auth.user?.first_name || 'مدیر' }}</div>
            <div class="text-white/40 text-xs">{{ auth.user?.phone }}</div>
          </div>
          <button @click="handleLogout" class="text-white/40 hover:text-lumia-gold transition-colors" title="خروج">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 lg:mr-64 flex flex-col min-h-screen">
      <!-- Top bar -->
      <header class="bg-white border-b border-base-200 px-4 py-4 flex items-center gap-3 sticky top-0 z-30">
        <button
          class="btn btn-ghost btn-sm btn-square lg:hidden flex-shrink-0"
          @click="sidebarOpen = !sidebarOpen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="flex-1 text-lumia-dark font-bold text-lg">{{ pageTitle }}</h1>
        <NuxtLink to="/" target="_blank" class="btn btn-ghost btn-sm gap-2 text-xs flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          <span class="hidden sm:inline">مشاهده سایت</span>
        </NuxtLink>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 lg:p-6 bg-base-200">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const sidebarOpen = ref(false)
watch(() => route.path, () => { sidebarOpen.value = false })

const pageTitles: Record<string, string> = {
  '/admin': 'داشبورد',
  '/admin/products': 'محصولات',
  '/admin/categories': 'دسته‌بندی‌ها',
  '/admin/brands': 'برندها',
  '/admin/orders': 'سفارشات',
  '/admin/users': 'کاربران',
  '/admin/coupons': 'کدهای تخفیف',
  '/admin/reviews': 'نظرات',
  '/admin/blog': 'وبلاگ',
  '/admin/instagram': 'اینستاگرام',
  '/admin/settings': 'تنظیمات',
  '/admin/settings/payment': 'درگاه پرداخت',
  '/admin/settings/sms': 'SMS و OTP',
  '/admin/sms/logs': 'لاگ پیامک',
}

const pageTitle = computed(() => {
  const path = route.path
  if (pageTitles[path]) return pageTitles[path]
  if (path.startsWith('/admin/settings/')) return 'تنظیمات'
  const parent = Object.keys(pageTitles)
    .filter(k => k !== '/admin' && path.startsWith(k + '/'))
    .sort((a, b) => b.length - a.length)[0]
  return parent ? pageTitles[parent] : 'پنل مدیریت'
})

async function handleLogout() {
  auth.logout()
  await router.push('/')
}
</script>
