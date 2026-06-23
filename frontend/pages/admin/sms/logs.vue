<template>
  <div>
    <NuxtLink to="/admin/settings" class="text-sm text-lumia-gold hover:underline mb-4 inline-block">
      ← بازگشت به تنظیمات
    </NuxtLink>

    <div class="bg-white rounded-2xl p-4 mb-4 border border-base-200 flex flex-wrap gap-3">
      <input v-model="filters.phone" type="tel" class="input input-bordered input-sm" placeholder="شماره" dir="ltr" />
      <select v-model="filters.status" class="select select-bordered select-sm">
        <option value="">همه وضعیت‌ها</option>
        <option value="sent">ارسال شده</option>
        <option value="simulated">شبیه‌سازی</option>
        <option value="failed">ناموفق</option>
      </select>
      <select v-model="filters.provider" class="select select-bordered select-sm">
        <option value="">همه provider</option>
        <option value="mock">mock</option>
        <option value="smsir">smsir</option>
      </select>
      <button class="btn btn-primary btn-sm" @click="load">فیلتر</button>
    </div>

    <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else class="bg-white rounded-2xl border border-base-200 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="table w-full">
          <thead class="bg-base-200/50">
            <tr class="text-xs text-lumia-dark/60">
              <th>زمان</th>
              <th>شماره</th>
              <th>Provider</th>
              <th>وضعیت</th>
              <th>قالب</th>
              <th>خطا</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="log in logs" :key="log.id">
              <tr class="hover:bg-base-200/30">
                <td class="text-xs">{{ formatDate(log.created_at) }}</td>
                <td dir="ltr" class="text-sm">{{ log.phone }}</td>
                <td class="text-sm">{{ log.provider }}</td>
                <td><span class="badge badge-sm" :class="statusClass(log.status)">{{ log.status }}</span></td>
                <td class="text-sm">{{ log.template_name || '—' }}</td>
                <td class="text-xs text-error max-w-[120px] truncate">{{ log.error_message || '—' }}</td>
                <td>
                  <button class="btn btn-ghost btn-xs" @click="toggleExpand(log.id)">جزئیات</button>
                </td>
              </tr>
              <tr v-if="expanded === log.id">
                <td colspan="7" class="bg-base-200/20 p-4">
                  <pre class="text-xs overflow-auto max-h-40">{{ JSON.stringify({ request: log.request_data, response: log.response_data }, null, 2) }}</pre>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <div v-if="!logs.length" class="p-8 text-center text-lumia-dark/40">لاگی یافت نشد</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PaginatedResponse, SmsLog } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatDate } = useApi()
const loading = ref(true)
const logs = ref<SmsLog[]>([])
const expanded = ref<string | null>(null)
const filters = ref({ phone: '', status: '', provider: '' })

function statusClass(status: string) {
  if (status === 'sent') return 'badge-success'
  if (status === 'simulated') return 'badge-info'
  return 'badge-error'
}

function toggleExpand(id: string) {
  expanded.value = expanded.value === id ? null : id
}

async function load() {
  loading.value = true
  const query: Record<string, string> = {}
  if (filters.value.phone) query.phone = filters.value.phone
  if (filters.value.status) query.status = filters.value.status
  if (filters.value.provider) query.provider = filters.value.provider
  const res = await apiFetch<PaginatedResponse<SmsLog>>('/admin/sms/logs/', { query })
  logs.value = res.results || (res as unknown as SmsLog[])
  loading.value = false
}

onMounted(load)
</script>
