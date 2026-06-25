<template>
  <div class="min-w-0 max-w-full">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
      <h2 class="font-bold text-lumia-dark">انبار و موجودی</h2>
      <button class="btn btn-ghost btn-sm" :class="{ loading }" @click="refresh">بروزرسانی</button>
    </div>

    <!-- Summary cards -->
    <div v-if="summary" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-2xl p-4 border border-base-200">
        <div class="text-xs text-lumia-dark/50">ناموجود</div>
        <div class="text-2xl font-bold text-error">{{ summary.out_of_stock }}</div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-base-200">
        <div class="text-xs text-lumia-dark/50">کم‌موجود</div>
        <div class="text-2xl font-bold text-warning">{{ summary.low_stock }}</div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-base-200">
        <div class="text-xs text-lumia-dark/50">سالم</div>
        <div class="text-2xl font-bold text-success">{{ summary.healthy }}</div>
      </div>
      <div class="bg-white rounded-2xl p-4 border border-base-200">
        <div class="text-xs text-lumia-dark/50">کل SKU فعال</div>
        <div class="text-2xl font-bold text-lumia-dark">{{ summary.total }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl p-4 border border-base-200 mb-4 flex flex-wrap gap-3 items-end">
      <div class="flex-1 min-w-[180px]">
        <label class="label-text text-xs block mb-1">جستجو</label>
        <input v-model="filters.q" type="text" class="input input-bordered input-sm w-full" placeholder="نام یا SKU" @keyup.enter="load" />
      </div>
      <div>
        <label class="label-text text-xs block mb-1">وضعیت</label>
        <select v-model="filters.status" class="select select-bordered select-sm" @change="load">
          <option value="all">همه</option>
          <option value="out">ناموجود</option>
          <option value="low">کم‌موجود</option>
          <option value="ok">سالم</option>
        </select>
      </div>
      <div>
        <label class="label-text text-xs block mb-1">دسته</label>
        <select v-model="filters.category" class="select select-bordered select-sm" @change="load">
          <option value="">همه</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div>
        <label class="label-text text-xs block mb-1">برند</label>
        <select v-model="filters.brand" class="select select-bordered select-sm" @change="load">
          <option value="">همه</option>
          <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
        </select>
      </div>
      <div>
        <label class="label-text text-xs block mb-1">آستانه کم‌موجود</label>
        <input v-model.number="filters.threshold" type="number" min="1" class="input input-bordered input-sm w-20" dir="ltr" @change="load" />
      </div>
      <button class="btn btn-primary btn-sm" @click="load">اعمال</button>
    </div>

    <div v-if="loading" class="text-center py-12 text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else-if="!items.length" class="bg-white rounded-2xl p-12 text-center text-lumia-dark/50 border border-base-200">
      محصولی با این فیلتر یافت نشد
    </div>

    <template v-else>
      <div class="lg:hidden space-y-3">
        <div v-for="item in items" :key="item.id" class="bg-white rounded-2xl p-4 border border-base-200">
          <div class="flex gap-3">
            <AppImage v-if="item.primary_image" :src="item.primary_image" alt="" img-class="w-14 h-14 rounded-lg object-cover" />
            <div class="flex-1 min-w-0">
              <p class="font-bold text-sm truncate">{{ item.name }}</p>
              <p class="text-xs text-lumia-dark/50">{{ item.brand_name }} — {{ item.category_name }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="font-bold text-sm" :class="statusClass(item.stock_status)">{{ item.stock }} {{ item.stock_unit_label }}</span>
                <span class="badge badge-xs" :class="badgeClass(item.stock_status)">{{ statusLabel(item.stock_status) }}</span>
              </div>
              <p class="text-xs text-lumia-dark/40 mt-1">
                {{ item.pack_label }}: {{ item.effective_pack_sizes.filter(s => s > 1).join(', ') || '—' }}
              </p>
            </div>
          </div>
          <div class="flex gap-2 mt-3">
            <button class="btn btn-primary btn-xs rounded-full" @click="openAdjust(item)">تعدیل موجودی</button>
            <NuxtLink :to="`/admin/products/${item.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink>
          </div>
        </div>
      </div>

      <div class="hidden lg:block bg-white rounded-2xl border border-base-200 overflow-hidden">
        <table class="table w-full">
          <thead class="bg-base-200/50">
            <tr class="text-xs text-lumia-dark/60">
              <th class="text-right">محصول</th>
              <th class="text-right">SKU</th>
              <th class="text-right">موجودی</th>
              <th class="text-right">آستانه</th>
              <th class="text-right">بسته‌ها</th>
              <th class="text-right">وضعیت</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id" class="hover:bg-base-200/30">
              <td>
                <div class="flex items-center gap-2">
                  <AppImage v-if="item.primary_image" :src="item.primary_image" alt="" img-class="w-8 h-8 rounded object-cover" />
                  <span class="text-sm font-medium">{{ item.name }}</span>
                </div>
              </td>
              <td class="text-sm font-mono text-lumia-dark/50">{{ item.sku || '—' }}</td>
              <td class="text-sm font-bold">{{ item.stock }} {{ item.stock_unit_label }}</td>
              <td class="text-sm text-lumia-dark/60">{{ item.effective_threshold }}</td>
              <td class="text-xs text-lumia-dark/60">
                {{ item.pack_label }}: {{ item.effective_pack_sizes.join(', ') }}
              </td>
              <td><span class="badge badge-sm" :class="badgeClass(item.stock_status)">{{ statusLabel(item.stock_status) }}</span></td>
              <td class="flex gap-2 justify-end">
                <button class="btn btn-primary btn-xs rounded-full" @click="openAdjust(item)">تعدیل</button>
                <NuxtLink :to="`/admin/products/${item.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-4">
        <button class="btn btn-sm" :disabled="page <= 1" @click="page--; load()">قبلی</button>
        <span class="self-center text-sm text-lumia-dark/60">{{ page }} / {{ totalPages }}</span>
        <button class="btn btn-sm" :disabled="page >= totalPages" @click="page++; load()">بعدی</button>
      </div>
    </template>

    <!-- Recent movements -->
    <div class="mt-8 bg-white rounded-2xl border border-base-200 overflow-hidden">
      <div class="p-4 border-b border-base-200 font-bold text-sm">آخرین حرکات انبار</div>
      <div v-if="!movements.length" class="p-6 text-center text-sm text-lumia-dark/40">حرکتی ثبت نشده</div>

      <template v-else>
        <div class="lg:hidden divide-y divide-base-200">
          <div v-for="m in movements" :key="m.id" class="px-4 py-3 text-sm">
            <div class="font-medium">{{ m.product_name }}</div>
            <div class="flex flex-wrap gap-2 mt-1 text-xs">
              <span class="font-mono" :class="m.delta > 0 ? 'text-success' : 'text-error'" dir="ltr">{{ m.delta > 0 ? '+' : '' }}{{ m.delta }}</span>
              <span class="font-mono text-lumia-dark/50" dir="ltr">{{ m.stock_before }} → {{ m.stock_after }}</span>
              <span class="text-lumia-dark/50">{{ formatDate(m.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="hidden lg:block admin-table-wrap">
        <table class="table table-sm w-full">
        <thead>
          <tr class="text-xs text-lumia-dark/50">
            <th class="text-right">محصول</th>
            <th class="text-right">تغییر</th>
            <th class="text-right">قبل → بعد</th>
            <th class="text-right">بسته</th>
            <th class="text-right">زمان</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in movements" :key="m.id">
            <td class="text-sm">{{ m.product_name }}</td>
            <td class="text-sm font-mono" :class="m.delta > 0 ? 'text-success' : 'text-error'" dir="ltr">{{ m.delta > 0 ? '+' : '' }}{{ m.delta }}</td>
            <td class="text-xs font-mono" dir="ltr">{{ m.stock_before }} → {{ m.stock_after }}</td>
            <td class="text-xs">
              <span v-if="m.pack_size && m.pack_count">{{ m.pack_count }}×{{ m.pack_size }}</span>
              <span v-else>—</span>
            </td>
            <td class="text-xs text-lumia-dark/50">{{ formatDate(m.created_at) }}</td>
          </tr>
        </tbody>
      </table>
        </div>
      </template>
    </div>

    <AdminStockAdjustModal ref="adjustModal" :product="selectedProduct" @saved="onAdjusted" />
  </div>
</template>

<script setup lang="ts">
import type { InventoryProduct, InventorySummary, StockMovement } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatDate } = useApi()
const loading = ref(true)
const summary = ref<InventorySummary | null>(null)
const items = ref<InventoryProduct[]>([])
const movements = ref<StockMovement[]>([])
const categories = ref<{ id: string; name: string }[]>([])
const brands = ref<{ id: string; name: string }[]>([])
const page = ref(1)
const totalPages = ref(1)
const adjustModal = ref<{ open: (p: InventoryProduct) => void } | null>(null)
const selectedProduct = ref<InventoryProduct | null>(null)

const filters = reactive({
  q: '',
  status: 'all',
  category: '',
  brand: '',
  threshold: 5,
})

function statusLabel(s: string) {
  return { out: 'ناموجود', low: 'کم‌موجود', ok: 'سالم' }[s] || s
}

function badgeClass(s: string) {
  return { out: 'badge-error', low: 'badge-warning', ok: 'badge-success' }[s] || 'badge-ghost'
}

function statusClass(s: string) {
  return { out: 'text-error', low: 'text-warning', ok: 'text-lumia-dark' }[s] || ''
}

async function loadSummary() {
  try {
    summary.value = await apiFetch<InventorySummary>('/admin/inventory/summary/')
  } catch {
    summary.value = null
  }
}

async function loadMovements() {
  try {
    const data = await apiFetch<{ results: StockMovement[] }>('/admin/inventory/movements/', { query: { limit: 10 } })
    movements.value = data.results
  } catch {
    movements.value = []
  }
}

async function load() {
  loading.value = true
  try {
    const query: Record<string, string | number> = {
      page: page.value,
      page_size: 20,
      status: filters.status,
    }
    if (filters.q) query.q = filters.q
    if (filters.category) query.category = filters.category
    if (filters.brand) query.brand = filters.brand
    if (filters.threshold) query.threshold = filters.threshold

    const data = await apiFetch<{
      results: InventoryProduct[]
      total_pages: number
    }>('/admin/inventory/', { query })

    items.value = data.results
    totalPages.value = data.total_pages
  } catch {
    items.value = []
    totalPages.value = 1
  } finally {
    loading.value = false
  }
}

async function refresh() {
  await Promise.all([loadSummary(), load(), loadMovements()])
}

function openAdjust(item: InventoryProduct) {
  selectedProduct.value = item
  adjustModal.value?.open(item)
}

async function onAdjusted() {
  await refresh()
}

onMounted(async () => {
  const [cats, brs] = await Promise.all([
    apiFetch<any>('/admin/categories/'),
    apiFetch<any>('/admin/brands/'),
  ])
  categories.value = cats.results ?? cats
  brands.value = brs.results ?? brs
  await refresh()
})
</script>
