<template>
  <div>
    <!-- Stats grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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
    </div>

    <!-- Recent orders -->
    <div class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-base-200 flex items-center justify-between">
        <h2 class="font-bold text-lumia-dark">آخرین سفارشات</h2>
        <NuxtLink to="/admin/orders" class="text-lumia-gold text-sm hover:underline">مشاهده همه</NuxtLink>
      </div>

      <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

      <div v-else-if="stats?.recent_orders?.length" class="overflow-x-auto">
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

      <div v-else class="p-8 text-center text-lumia-dark/40">سفارشی ثبت نشده است</div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatPrice, formatDate } = useApi()

const stats = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    stats.value = await apiFetch('/admin/dashboard/')
  } finally {
    loading.value = false
  }
})
</script>
