<template>
  <div class="min-w-0 max-w-full">
    <!-- Quick purchase-code lookup: the seller's most-used action -->
    <form
      class="mb-6 flex flex-col gap-3 rounded-2xl border-2 border-lumia-gold/40 bg-gradient-to-bl from-lumia-gold/15 to-white p-4 sm:flex-row sm:items-center"
      @submit.prevent="goToLookup"
    >
      <div class="min-w-0 flex-1">
        <p class="font-black text-lumia-dark">پیگیری سریع کد خرید</p>
        <p class="text-xs text-lumia-dark/50">کد ۶ رقمی مشتری را وارد کنید تا اطلاعات سفارش باز شود.</p>
      </div>
      <input
        v-model="quickCode"
        class="input input-bordered w-full rounded-xl text-center font-mono text-xl font-black tracking-[0.3em] sm:w-52"
        dir="ltr"
        placeholder="------"
        inputmode="numeric"
      />
      <button type="submit" class="btn btn-primary rounded-xl px-6 font-bold" :disabled="!quickCode">جستجو</button>
    </form>

    <!-- Stats grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <AdminStatsCard label="سفارشات پرداخت‌شده جدید" :value="stats?.new_orders_count ?? '—'" colorClass="bg-green-100">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </template>
      </AdminStatsCard>

      <AdminStatsCard label="درآمد امروز" :value="formatPrice(stats?.today_income ?? 0)" colorClass="bg-lumia-gold/15">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-lumia-gold" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </template>
      </AdminStatsCard>

      <AdminStatsCard label="درآمد هفته" :value="formatPrice(stats?.weekly_income ?? 0)" colorClass="bg-blue-100">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </template>
      </AdminStatsCard>

      <AdminStatsCard label="کل سفارشات" :value="stats?.total_orders ?? '—'" colorClass="bg-purple-100">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </template>
      </AdminStatsCard>

      <AdminStatsCard label="کل کاربران" :value="stats?.total_users ?? '—'" colorClass="bg-teal-100">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-teal-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </template>
      </AdminStatsCard>

      <AdminStatsCard label="محصولات فعال" :value="stats?.total_products ?? '—'" colorClass="bg-orange-100">
        <template #icon>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </template>
      </AdminStatsCard>

      <NuxtLink to="/admin/inventory" class="block">
        <AdminStatsCard
          label="محصولات کم‌موجود"
          :value="stats?.low_stock_count ?? '—'"
          :colorClass="(stats?.low_stock_count ?? 0) > 0 ? 'bg-red-100' : 'bg-gray-100'"
        >
          <template #icon>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" :class="(stats?.low_stock_count ?? 0) > 0 ? 'text-red-600' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </template>
        </AdminStatsCard>
      </NuxtLink>
    </div>

    <!-- Revenue chart -->
    <div v-if="stats?.daily_revenue?.length" class="bg-white rounded-2xl shadow-sm border border-base-200 p-6 mb-6 min-w-0 overflow-hidden">
      <h2 class="font-bold text-lumia-dark mb-4">درآمد ۳۰ روز اخیر</h2>
      <div class="overflow-hidden min-w-0">
      <div class="flex items-end gap-1 h-40 overflow-x-auto min-w-0 w-full pb-2">
        <div
          v-for="day in stats.daily_revenue"
          :key="day.date"
          class="flex flex-col items-center gap-1 w-2 shrink-0"
          :title="`${day.date}: ${formatPrice(day.revenue)}`"
        >
          <div
            class="w-full bg-lumia-gold/80 rounded-t-sm min-h-[2px] transition-all"
            :style="{ height: `${barHeight(day.revenue)}%` }"
          />
        </div>
      </div>
      </div>
    </div>

    <!-- Top products -->
    <div v-if="stats?.top_products?.length" class="bg-white rounded-2xl shadow-sm border border-base-200 p-6 mb-6">
      <h2 class="font-bold text-lumia-dark mb-4">پرفروش‌ترین محصولات</h2>
      <div class="space-y-2">
        <div v-for="p in stats.top_products" :key="p.id" class="flex justify-between text-sm border-b border-base-100 pb-2">
          <NuxtLink :to="`/admin/products/${p.id}`" class="text-lumia-dark hover:text-lumia-gold">{{ p.name }}</NuxtLink>
          <span class="font-bold">{{ p.sales_count }} فروش</span>
        </div>
      </div>
    </div>

    <!-- Recent orders -->
    <div class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-base-200 flex items-center justify-between">
        <h2 class="font-bold text-lumia-dark">آخرین سفارشات</h2>
        <NuxtLink to="/admin/orders" class="text-lumia-gold text-sm hover:underline">مشاهده همه</NuxtLink>
      </div>

      <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

      <template v-else-if="stats?.recent_orders?.length">
        <div class="lg:hidden divide-y divide-base-200">
          <div v-for="order in stats.recent_orders" :key="order.id" class="px-4 py-3 flex flex-wrap items-center justify-between gap-2">
            <div class="min-w-0">
              <div class="text-sm font-mono font-medium">{{ order.order_number }}</div>
              <div class="text-xs text-lumia-dark/50">{{ order.user_phone }}</div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <AdminBadge :status="order.status" />
              <span class="text-sm font-bold">{{ formatPrice(order.total) }}</span>
              <NuxtLink :to="`/admin/orders/${order.id}`" class="btn btn-ghost btn-xs text-lumia-gold">جزئیات</NuxtLink>
            </div>
          </div>
        </div>

        <div class="hidden lg:block admin-table-wrap">
        <table class="table w-full">
          <thead class="bg-base-200/50">
            <tr class="text-lumia-dark/60 text-xs">
              <th class="font-medium text-right">شماره سفارش</th>
              <th class="font-medium text-right">خریدار</th>
              <th class="font-medium text-right">وضعیت</th>
              <th class="font-medium text-right">مبلغ</th>
              <th class="font-medium text-right">تاریخ</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in stats.recent_orders" :key="order.id" class="hover:bg-base-200/30 transition-colors">
              <td class="text-sm font-mono">{{ order.order_number }}</td>
              <td class="text-sm">{{ order.user_phone }}</td>
              <td><AdminBadge :status="order.status" /></td>
              <td class="text-sm font-bold">{{ formatPrice(order.total) }}</td>
              <td class="text-sm text-lumia-dark/50">{{ formatDate(order.created_at) }}</td>
              <td>
                <NuxtLink :to="`/admin/orders/${order.id}`" class="btn btn-ghost btn-xs text-lumia-gold">جزئیات</NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </template>

      <div v-else class="p-8 text-center text-lumia-dark/40">سفارشی ثبت نشده است</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminDashboardStats } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatPrice, formatDate } = useApi()

const stats = ref<AdminDashboardStats | null>(null)
const loading = ref(true)

const quickCode = ref('')

function goToLookup() {
  const code = quickCode.value
    .replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))
    .replace(/[^0-9a-zA-Z]/g, '')
    .toUpperCase()
  if (!code) return
  navigateTo({ path: '/admin/lookup', query: { code } })
}

const maxRevenue = computed(() => {
  if (!stats.value?.daily_revenue?.length) return 1
  return Math.max(...stats.value.daily_revenue.map(d => d.revenue), 1)
})

function barHeight(revenue: number) {
  return Math.max(4, Math.round((revenue / maxRevenue.value) * 100))
}

onMounted(async () => {
  try {
    stats.value = await apiFetch<AdminDashboardStats>('/admin/dashboard/')
  } finally {
    loading.value = false
  }
})
</script>
