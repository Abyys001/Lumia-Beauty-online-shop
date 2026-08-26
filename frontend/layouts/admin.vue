<template>
  <div data-theme="lumia" class="admin-layout min-h-screen w-full max-w-[100vw] overflow-x-clip relative" dir="rtl">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'w-64 max-w-[85vw] h-dvh bg-lumia-dark text-lumia-light flex flex-col fixed top-0 z-40 transition-[right] duration-300 lg:right-0',
        sidebarOpen ? 'right-0' : 'max-lg:-right-64 lg:right-0'
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
        <AdminNavItem to="/admin/lookup" icon="lookup" label="پیگیری کد خرید" :badge="summary?.awaiting_payment" />
        <AdminNavItem to="/admin/products" icon="products" label="محصولات" />
        <AdminNavItem to="/admin/categories" icon="categories" label="دسته‌بندی‌ها" />
        <AdminNavItem to="/admin/brands" icon="brands" label="برندها" />
        <AdminNavItem to="/admin/orders" icon="orders" label="سفارشات" :badge="summary?.pending_orders" />
        <AdminNavItem to="/admin/inventory" icon="products" label="انبار" :badge="summary?.low_stock_count" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">مدیریت</div>
        <AdminNavItem to="/admin/users" icon="users" label="کاربران" />
        <AdminNavItem to="/admin/coupons" icon="coupons" label="کدهای تخفیف" />
        <AdminNavItem to="/admin/reviews" icon="reviews" label="نظرات" :badge="summary?.pending_reviews" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">محتوا</div>
        <AdminNavItem to="/admin/blog" icon="blog" label="وبلاگ" />
        <AdminNavItem to="/admin/instagram" icon="instagram" label="پیج‌های اینستاگرام" />
        <AdminNavItem to="/admin/cms" icon="blog" label="صفحه اصلی" />

        <div class="px-4 mt-4 mb-2 text-white/30 text-xs font-medium tracking-wider">سیستم</div>
        <AdminNavItem to="/admin/settings" icon="settings" label="تنظیمات" :exact="true" />
      </nav>

      <!-- User -->
      <div class="px-4 py-4 border-t border-white/10">
        <ClientOnly>
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
          <template #fallback>
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-lumia-gold/20 skeleton" />
              <div class="flex-1 min-w-0 space-y-1">
                <div class="h-3 w-16 skeleton rounded" />
                <div class="h-3 w-24 skeleton rounded" />
              </div>
            </div>
          </template>
        </ClientOnly>
      </div>
    </aside>

    <!-- Main content -->
    <div class="min-w-0 lg:mr-64 flex flex-col min-h-screen">
      <!-- Top bar -->
      <header class="bg-white border-b border-base-200 px-4 py-4 flex items-center gap-3 sticky top-0 z-30 min-w-0">
        <PageBack variant="icon" />
        <button
          class="btn btn-ghost btn-sm btn-square lg:hidden flex-shrink-0"
          @click="sidebarOpen = !sidebarOpen"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="flex-1 text-lumia-dark font-bold text-lg truncate min-w-0">{{ pageTitle }}</h1>
        <NuxtLink to="/" target="_blank" class="btn btn-ghost btn-sm gap-2 text-xs flex-shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          <span class="hidden sm:inline">مشاهده سایت</span>
        </NuxtLink>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 lg:p-6 bg-base-200 min-w-0 max-w-full overflow-x-clip">
        <div class="admin-page min-w-0 max-w-full">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const { summary } = useAdminNotifications()

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
  '/admin/instagram': 'پیج‌های اینستاگرام',
  '/admin/cms': 'صفحه اصلی',
  '/admin/inventory': 'انبار',
  '/admin/settings': 'تنظیمات',
  '/admin/settings/payment': 'درگاه پرداخت',
  '/admin/settings/shipping': 'هزینه ارسال',
  '/admin/settings/contact': 'اطلاعات تماس',
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
  await auth.signOut()
  await router.push('/')
}
</script>
