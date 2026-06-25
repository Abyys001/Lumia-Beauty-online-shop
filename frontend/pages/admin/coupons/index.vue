<template>
  <div>
    <div class="flex justify-end mb-5">
      <NuxtLink to="/admin/coupons/new" class="btn btn-primary btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        کد تخفیف جدید
      </NuxtLink>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div
          v-for="coupon in coupons"
          :key="coupon.id"
          class="bg-white rounded-xl p-3 border border-base-200"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="font-mono text-sm font-bold">{{ coupon.code }}</div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/60 flex-wrap">
                <span class="badge badge-ghost badge-sm">{{ typeLabel(coupon.coupon_type) }}</span>
                <span class="font-medium text-lumia-gold">
                  {{ coupon.coupon_type === 'percent' ? coupon.value + '%' : formatPrice(coupon.value) }}
                </span>
              </div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/40 flex-wrap">
                <span>استفاده: {{ coupon.used_count }} / {{ coupon.max_uses ?? '∞' }}</span>
                <span v-if="coupon.valid_until">· انقضا: {{ formatDate(coupon.valid_until) }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="coupon.is_active" @change="toggleActive(coupon, $event)" />
              <NuxtLink :to="`/admin/coupons/${coupon.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">کد</th>
                <th class="font-medium text-right">نوع</th>
                <th class="font-medium text-right">مقدار</th>
                <th class="font-medium text-right">حداقل سفارش</th>
                <th class="font-medium text-right">استفاده</th>
                <th class="font-medium text-right">انقضا</th>
                <th class="font-medium text-right">فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="coupon in coupons" :key="coupon.id" class="hover:bg-base-200/30">
                <td class="font-mono text-sm font-bold">{{ coupon.code }}</td>
                <td class="text-sm">{{ typeLabel(coupon.coupon_type) }}</td>
                <td class="text-sm">{{ coupon.coupon_type === 'percent' ? coupon.value + '%' : formatPrice(coupon.value) }}</td>
                <td class="text-sm">{{ formatPrice(coupon.min_order_amount) }}</td>
                <td class="text-sm">{{ coupon.used_count }} / {{ coupon.max_uses ?? '∞' }}</td>
                <td class="text-sm text-lumia-dark/50">{{ coupon.valid_until ? formatDate(coupon.valid_until) : '—' }}</td>
                <td><input type="checkbox" class="toggle toggle-success toggle-sm" :checked="coupon.is_active" @change="toggleActive(coupon, $event)" /></td>
                <td><NuxtLink :to="`/admin/coupons/${coupon.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatPrice, formatDate } = useApi()
const coupons = ref<any[]>([])
const loading = ref(true)

const typeLabels: Record<string, string> = { percent: 'درصدی', fixed: 'مبلغ ثابت', free_shipping: 'ارسال رایگان' }
const typeLabel = (t: string) => typeLabels[t] ?? t

async function load() {
  loading.value = true
  const res = await apiFetch<any>('/admin/coupons/')
  coupons.value = res.results ?? res
  loading.value = false
}

async function toggleActive(coupon: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/coupons/${coupon.id}/`, { method: 'PATCH', body: { is_active: val } })
  coupon.is_active = val
}

onMounted(load)
</script>
