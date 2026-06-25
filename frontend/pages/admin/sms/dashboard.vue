<template>
  <div class="max-w-4xl space-y-4">
    <div v-if="status?.is_sandbox && isSmsIr" class="alert alert-warning text-sm">
      حالت Sandbox فعال است — گزارش‌ها در SMS.ir ثبت نمی‌شوند.
    </div>
    <div v-if="isIranPayamak && !status?.has_bearer_token" class="alert alert-info text-sm">
      برای دریافت لیست خطوط از پنل، در تنظیمات SMS وارد شوید (Login + 2FA). ارسال OTP فقط به Api-Key و شماره خط نیاز دارد.
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="bg-white rounded-2xl p-5 border border-base-200">
          <div class="text-xs text-lumia-dark/50 mb-1">اعتبار {{ isIranPayamak ? '(تومان)' : '' }}</div>
          <div class="text-2xl font-bold text-lumia-dark">{{ credit ?? '—' }}</div>
          <div v-if="status?.balance_count != null" class="text-xs text-lumia-dark/50 mt-1">
            معادل {{ status.balance_count }} پیامک
          </div>
        </div>
        <div class="bg-white rounded-2xl p-5 border border-base-200">
          <div class="text-xs text-lumia-dark/50 mb-1">محیط</div>
          <div class="flex gap-2 mt-1 flex-wrap">
            <span class="badge" :class="runtimeBadgeClass">{{ runtimeLabel }}</span>
            <span v-if="status?.is_sandbox && isSmsIr" class="badge badge-warning">Sandbox</span>
            <span v-else-if="status?.runtime_provider !== 'mock'" class="badge badge-primary">Production</span>
          </div>
          <div v-if="isIranPayamak && status?.line_number" class="text-xs mt-2" dir="ltr">
            خط: {{ status.line_number }}
          </div>
        </div>
        <div class="bg-white rounded-2xl p-5 border border-base-200">
          <div class="text-xs text-lumia-dark/50 mb-1">آخرین تست</div>
          <div class="text-sm">{{ status?.last_test_message || '—' }}</div>
        </div>
      </div>

      <div v-if="status?.balance_details?.length" class="bg-white rounded-2xl p-5 border border-base-200">
        <h2 class="font-bold text-lumia-dark text-sm mb-2">جزئیات موجودی</h2>
        <ul class="text-sm space-y-1">
          <li v-for="(d, i) in status.balance_details" :key="i" dir="ltr">
            {{ d.count }} پیامک × {{ d.rate }} = {{ d.amount }} تومان
          </li>
        </ul>
      </div>

      <div class="bg-white rounded-2xl p-6 border border-base-200 space-y-3">
        <h2 class="font-bold text-lumia-dark">خطوط ارسال</h2>
        <div v-if="status?.is_sandbox && isSmsIr" class="text-sm text-warning">در Sandbox خطوط نمایش داده نمی‌شوند.</div>
        <div v-else-if="isIranPayamak && !status?.has_bearer_token" class="text-sm text-warning">
          Bearer token موجود نیست — از تنظیمات SMS وارد پنل شوید.
        </div>
        <div v-else-if="linesLoading" class="text-sm text-lumia-dark/40">در حال بارگذاری...</div>
        <ul v-else-if="lines.length" class="text-sm space-y-2">
          <li v-for="(line, i) in lines" :key="i" class="rounded-lg bg-base-200/40 px-3 py-2" dir="ltr">
            {{ formatLine(line) }}
          </li>
        </ul>
        <div v-else class="text-sm text-lumia-dark/40">خطی یافت نشد یا خطا در دریافت</div>
        <button
          class="btn btn-outline btn-sm"
          :class="{ loading: linesLoading }"
          :disabled="(status?.is_sandbox && isSmsIr) || (isIranPayamak && !status?.has_bearer_token)"
          @click="loadLines"
        >
          بروزرسانی خطوط
        </button>
      </div>

      <div class="flex flex-wrap gap-2">
        <NuxtLink to="/admin/settings/sms" class="btn btn-primary btn-sm">تنظیمات SMS</NuxtLink>
        <NuxtLink to="/admin/sms/test-send" class="btn btn-outline btn-sm">ارسال تست</NuxtLink>
        <NuxtLink v-if="isSmsIr" to="/admin/sms/reports" class="btn btn-outline btn-sm">گزارش‌ها</NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SmsApiResult, SmsProviderStatus } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const linesLoading = ref(false)
const status = ref<SmsProviderStatus | null>(null)
const credit = ref<number | null>(null)
const lines = ref<unknown[]>([])

const isIranPayamak = computed(() => status.value?.runtime_provider === 'iranpayamak')
const isSmsIr = computed(() => status.value?.runtime_provider === 'smsir')
const runtimeLabel = computed(() => {
  const r = status.value?.runtime_provider
  if (r === 'iranpayamak') return 'IranPayamak'
  if (r === 'smsir') return 'SMS.ir'
  return 'Mock'
})
const runtimeBadgeClass = computed(() =>
  status.value?.runtime_provider === 'mock' ? 'badge-ghost' : 'badge-success',
)

function formatLine(line: unknown): string {
  if (line == null) return '—'
  if (typeof line === 'string' || typeof line === 'number') return String(line)
  if (typeof line === 'object') {
    const obj = line as Record<string, unknown>
    const num = obj.number ?? obj.line_number ?? obj.lineNumber ?? obj.mobile
    const label = obj.title ?? obj.name ?? obj.type
    if (num) return label ? `${num} (${label})` : String(num)
    return JSON.stringify(line)
  }
  return String(line)
}

async function loadLines() {
  if (status.value?.is_sandbox && isSmsIr.value) return
  if (isIranPayamak.value && !status.value?.has_bearer_token) return
  linesLoading.value = true
  try {
    const res = await apiFetch<SmsApiResult>('/admin/sms/lines/')
    lines.value = Array.isArray(res.data) ? res.data : res.data ? [res.data] : []
  } catch {
    lines.value = []
  } finally {
    linesLoading.value = false
  }
}

onMounted(async () => {
  try {
    const [st, cr] = await Promise.all([
      apiFetch<SmsProviderStatus>('/admin/sms/provider/status/'),
      apiFetch<SmsApiResult>('/admin/sms/credit/'),
    ])
    status.value = st
    credit.value = cr.credit ?? st.credit
    const canLoadLines = !(st.is_sandbox && st.runtime_provider === 'smsir')
      && !(st.runtime_provider === 'iranpayamak' && !st.has_bearer_token)
    if (canLoadLines) await loadLines()
  } finally {
    loading.value = false
  }
})
</script>
