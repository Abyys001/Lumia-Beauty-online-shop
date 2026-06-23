<template>
  <div>
    <!-- Filters -->
    <div class="flex flex-wrap gap-3 mb-5">
      <input v-model="search" type="text" placeholder="جستجو شماره سفارش / شماره تلفن..." class="input input-bordered input-sm w-64" @input="debouncedFetch" />
      <select v-model="filterStatus" class="select select-bordered select-sm" @change="fetchOrders">
        <option value="">همه وضعیت‌ها</option>
        <option value="pending">در انتظار پرداخت</option>
        <option value="paid">پرداخت شده</option>
        <option value="processing">در حال پردازش</option>
        <option value="shipped">ارسال شده</option>
        <option value="delivered">تحویل داده شده</option>
        <option value="cancelled">لغو شده</option>
        <option value="refunded">مرجوع شده</option>
      </select>
      <input v-model="dateFrom" type="date" class="input input-bordered input-sm" @change="fetchOrders" dir="ltr" />
      <input v-model="dateTo" type="date" class="input input-bordered input-sm" @change="fetchOrders" dir="ltr" />
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>
      <div v-else class="overflow-x-auto">
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
            <tr v-for="order in orders" :key="order.id" class="hover:bg-base-200/30 transition-colors">
              <td class="font-mono text-sm">{{ order.order_number }}</td>
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

      <div v-if="totalCount > 0" class="px-6 py-4 border-t border-base-200 flex items-center justify-between">
        <span class="text-sm text-lumia-dark/50">{{ totalCount }} سفارش</span>
        <div class="flex gap-2">
          <button class="btn btn-ghost btn-sm" :disabled="!prevPage" @click="goToPage(currentPage - 1)">قبلی</button>
          <span class="btn btn-ghost btn-sm pointer-events-none">{{ currentPage }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="!nextPage" @click="goToPage(currentPage + 1)">بعدی</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatPrice, formatDate } = useApi()

const search = ref('')
const filterStatus = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const orders = ref<any[]>([])
const loading = ref(true)
const totalCount = ref(0)
const nextPage = ref<string | null>(null)
const prevPage = ref<string | null>(null)
const currentPage = ref(1)

async function fetchOrders() {
  loading.value = true
  try {
    const params: Record<string, string> = { page: String(currentPage.value) }
    if (search.value) params.search = search.value
    if (filterStatus.value) params.status = filterStatus.value
    if (dateFrom.value) params.date_from = dateFrom.value
    if (dateTo.value) params.date_to = dateTo.value
    const res = await apiFetch<any>('/admin/orders/', { params })
    orders.value = res.results
    totalCount.value = res.count
    nextPage.value = res.next
    prevPage.value = res.previous
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) { currentPage.value = page; fetchOrders() }

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; fetchOrders() }, 350)
}

onMounted(fetchOrders)
</script>
