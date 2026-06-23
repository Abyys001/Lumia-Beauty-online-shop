<template>
  <div>
    <div class="flex gap-3 mb-5">
      <select v-model="filterApproved" class="select select-bordered select-sm" @change="load">
        <option value="">همه نظرات</option>
        <option value="false">در انتظار تأیید</option>
        <option value="true">تأیید شده</option>
      </select>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div
          v-for="review in reviews"
          :key="review.id"
          class="bg-white rounded-xl p-3 border border-base-200"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium truncate">{{ review.product_name }}</div>
              <div class="flex items-center gap-2 mt-1">
                <span class="font-mono text-xs text-lumia-dark/50">{{ review.user_phone }}</span>
                <div class="flex gap-0.5">
                  <span v-for="i in 5" :key="i" class="text-xs" :class="i <= review.rating ? 'text-warning' : 'text-base-300'">★</span>
                </div>
              </div>
              <p class="text-xs text-lumia-dark/60 mt-1 line-clamp-2">{{ review.comment }}</p>
              <div class="text-xs text-lumia-dark/40 mt-1">{{ formatDate(review.created_at) }}</div>
            </div>
            <div class="flex-shrink-0 pt-0.5">
              <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="review.is_approved" @change="toggleApprove(review, $event)" />
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">محصول</th>
                <th class="font-medium text-right">کاربر</th>
                <th class="font-medium text-right">امتیاز</th>
                <th class="font-medium text-right">نظر</th>
                <th class="font-medium text-right">تاریخ</th>
                <th class="font-medium text-right">تأیید</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="review in reviews" :key="review.id" class="hover:bg-base-200/30">
                <td class="text-sm">{{ review.product_name }}</td>
                <td class="text-sm font-mono">{{ review.user_phone }}</td>
                <td>
                  <div class="flex gap-0.5">
                    <span v-for="i in 5" :key="i" class="text-xs" :class="i <= review.rating ? 'text-warning' : 'text-base-300'">★</span>
                  </div>
                </td>
                <td class="text-sm max-w-xs"><p class="truncate">{{ review.comment }}</p></td>
                <td class="text-sm text-lumia-dark/50">{{ formatDate(review.created_at) }}</td>
                <td><input type="checkbox" class="toggle toggle-success toggle-sm" :checked="review.is_approved" @change="toggleApprove(review, $event)" /></td>
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

const { apiFetch, formatDate } = useApi()
const reviews = ref<any[]>([])
const loading = ref(true)
const filterApproved = ref('')

async function load() {
  loading.value = true
  const params: Record<string, string> = {}
  if (filterApproved.value) params.is_approved = filterApproved.value
  const res = await apiFetch<any>('/admin/reviews/', { params })
  reviews.value = res.results ?? res
  loading.value = false
}

async function toggleApprove(review: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/reviews/${review.id}/`, { method: 'PATCH', body: { is_approved: val } })
  review.is_approved = val
}

onMounted(load)
</script>
