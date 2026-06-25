<template>
  <div>
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline mb-4 inline-block">
      ← داشبورد SMS
    </NuxtLink>

    <div v-if="isSandbox" class="alert alert-warning text-sm mb-4">
      Sandbox: گزارش دلیوری از SMS.ir در دسترس نیست — فقط لاگ محلی نمایش داده می‌شود.
    </div>

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
      <div class="overflow-x-auto w-full min-w-0">
        <table class="table w-full">
          <thead class="bg-base-200/50">
            <tr class="text-xs text-lumia-dark/60">
              <th>زمان</th>
              <th>شماره</th>
              <th>API mobile</th>
              <th>Provider</th>
              <th>وضعیت</th>
              <th>خطا</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="log in logs" :key="log.id">
              <tr class="hover:bg-base-200/30">
                <td class="text-xs">{{ formatDate(log.created_at) }}</td>
                <td dir="ltr" class="text-sm">{{ log.phone }}</td>
                <td dir="ltr" class="text-xs font-mono">{{ apiMobile(log) }}</td>
                <td class="text-sm">{{ log.provider }}</td>
                <td><span class="badge badge-sm" :class="statusClass(log.status)">{{ log.status }}</span></td>
                <td class="text-xs text-error max-w-[140px] truncate">{{ log.error_message || '—' }}</td>
                <td class="flex gap-1">
                  <button class="btn btn-ghost btn-xs" @click="toggleExpand(log.id)">جزئیات</button>
                  <button
                    v-if="log.provider_message_id && !isSandbox"
                    class="btn btn-ghost btn-xs text-lumia-gold"
                    @click="fetchDelivery(log)"
                  >
                    دلیوری
                  </button>
                </td>
              </tr>
              <tr v-if="expanded === log.id">
                <td colspan="7" class="bg-base-200/20 p-4 space-y-2">
                  <pre class="text-xs overflow-auto max-h-40" dir="ltr">{{ JSON.stringify({ request: log.request_data, response: log.response_data }, null, 2) }}</pre>
                  <div v-if="deliveryReports[log.id]" class="text-xs">
                    <strong>دلیوری:</strong> {{ deliveryReports[log.id]?.delivery_state_label || deliveryReports[log.id]?.message }}
                  </div>
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
import type { PaginatedResponse, SmsApiResult, SmsLog, SmsProviderStatus } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatDate, extractApiError } = useApi()
const loading = ref(true)
const isSandbox = ref(false)
const logs = ref<SmsLog[]>([])
const expanded = ref<string | null>(null)
const deliveryReports = ref<Record<string, SmsApiResult>>({})
const filters = ref({ phone: '', status: '', provider: '' })

function statusClass(status: string) {
  if (status === 'sent') return 'badge-success'
  if (status === 'simulated') return 'badge-info'
  return 'badge-error'
}

function apiMobile(log: SmsLog) {
  const m = log.request_data?.mobile
  return m != null ? String(m) : '—'
}

function toggleExpand(id: string) {
  expanded.value = expanded.value === id ? null : id
}

async function fetchDelivery(log: SmsLog) {
  if (!log.provider_message_id) return
  expanded.value = log.id
  try {
    deliveryReports.value[log.id] = await apiFetch<SmsApiResult>(
      `/admin/sms/reports/message/${log.provider_message_id}/`,
    )
  } catch (e: unknown) {
    deliveryReports.value[log.id] = { success: false, error_hint: extractApiError(e, 'خطا') }
  }
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

onMounted(async () => {
  const st = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  isSandbox.value = st.is_sandbox
  await load()
})
</script>
