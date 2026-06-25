<template>
  <div class="max-w-4xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline">← داشبورد SMS</NuxtLink>

    <div v-if="isSandbox" class="alert alert-warning text-sm">
      در Sandbox گزارش ارسال در SMS.ir ثبت نمی‌شود — این بخش فقط در Production کار می‌کند.
    </div>

    <div role="tablist" class="tabs tabs-boxed bg-white p-1 rounded-xl border border-base-200 w-fit">
      <button v-for="t in tabs" :key="t.id" class="tab" :class="{ 'tab-active': tab === t.id }" @click="tab = t.id">{{ t.label }}</button>
    </div>

    <!-- Message report -->
    <div v-if="tab === 'message'" class="bg-white rounded-2xl p-6 border border-base-200 space-y-4">
      <h2 class="font-bold">گزارش پیامک (messageId)</h2>
      <div class="flex gap-2">
        <input v-model="messageId" type="number" class="input input-bordered input-sm" dir="ltr" placeholder="89545112" />
        <button class="btn btn-primary btn-sm" :class="{ loading: loading }" :disabled="isSandbox" @click="loadMessage">دریافت</button>
      </div>
      <pre v-if="report" class="text-xs bg-base-200/40 p-4 rounded-xl overflow-auto max-h-96" dir="ltr">{{ JSON.stringify(report, null, 2) }}</pre>
      <p v-if="report?.delivery_state_label" class="text-sm">وضعیت دلیوری: <strong>{{ report.delivery_state_label }}</strong></p>
    </div>

    <!-- Live -->
    <div v-else-if="tab === 'live'" class="bg-white rounded-2xl p-6 border border-base-200 space-y-4">
      <h2 class="font-bold">ارسال‌های امروز (live)</h2>
      <button class="btn btn-primary btn-sm" :class="{ loading: loading }" :disabled="isSandbox" @click="loadLive">بارگذاری</button>
      <pre v-if="liveData" class="text-xs bg-base-200/40 p-4 rounded-xl overflow-auto max-h-96" dir="ltr">{{ JSON.stringify(liveData, null, 2) }}</pre>
    </div>

    <!-- Packs -->
    <div v-else class="bg-white rounded-2xl p-6 border border-base-200 space-y-4">
      <h2 class="font-bold">بسته‌های ارسال</h2>
      <button class="btn btn-primary btn-sm" :class="{ loading: loading }" :disabled="isSandbox" @click="loadPacks">لیست بسته‌ها</button>
      <pre v-if="packsData" class="text-xs bg-base-200/40 p-4 rounded-xl overflow-auto max-h-48" dir="ltr">{{ JSON.stringify(packsData, null, 2) }}</pre>
      <div v-if="packsData?.data?.length" class="flex gap-2 items-center">
        <input v-model="packId" class="input input-bordered input-sm flex-1" dir="ltr" placeholder="packId" />
        <button class="btn btn-outline btn-sm" :disabled="!packId || isSandbox" @click="loadPackDetail">جزئیات</button>
      </div>
      <pre v-if="packDetail" class="text-xs bg-base-200/40 p-4 rounded-xl overflow-auto max-h-96" dir="ltr">{{ JSON.stringify(packDetail, null, 2) }}</pre>
    </div>

    <div v-if="error" class="text-sm text-error">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import type { SmsApiResult, SmsProviderStatus } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, extractApiError } = useApi()
const tabs = [
  { id: 'message', label: 'گزارش پیام' },
  { id: 'live', label: 'ارسال‌های امروز' },
  { id: 'packs', label: 'بسته‌ها' },
] as const
type TabId = typeof tabs[number]['id']

const tab = ref<TabId>('message')
const isSandbox = ref(false)
const loading = ref(false)
const error = ref('')
const messageId = ref('')
const packId = ref('')
const report = ref<SmsApiResult | null>(null)
const liveData = ref<SmsApiResult | null>(null)
const packsData = ref<SmsApiResult | null>(null)
const packDetail = ref<SmsApiResult | null>(null)

onMounted(async () => {
  const st = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  isSandbox.value = st.is_sandbox
})

async function loadMessage() {
  loading.value = true
  error.value = ''
  try {
    report.value = await apiFetch<SmsApiResult>(`/admin/sms/reports/message/${messageId.value}/`)
  } catch (e: unknown) {
    error.value = extractApiError(e, 'خطا')
  } finally { loading.value = false }
}

async function loadLive() {
  loading.value = true
  error.value = ''
  try {
    liveData.value = await apiFetch<SmsApiResult>('/admin/sms/reports/live/')
  } catch (e: unknown) {
    error.value = extractApiError(e, 'خطا')
  } finally { loading.value = false }
}

async function loadPacks() {
  loading.value = true
  error.value = ''
  try {
    packsData.value = await apiFetch<SmsApiResult>('/admin/sms/reports/packs/')
  } catch (e: unknown) {
    error.value = extractApiError(e, 'خطا')
  } finally { loading.value = false }
}

async function loadPackDetail() {
  error.value = ''
  try {
    packDetail.value = await apiFetch<SmsApiResult>(`/admin/sms/reports/packs/${packId.value}/`)
  } catch (e: unknown) {
    error.value = extractApiError(e, 'خطا')
  }
}
</script>
