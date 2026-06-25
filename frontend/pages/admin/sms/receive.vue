<template>
  <div class="max-w-4xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline">← داشبورد SMS</NuxtLink>

    <div v-if="isSandbox" class="alert alert-warning text-sm">
      در Sandbox پیامک دریافتی ثبت نمی‌شود.
    </div>

    <div class="bg-white rounded-2xl p-6 border border-base-200 space-y-4">
      <h2 class="font-bold text-lumia-dark">آخرین پیامک‌های دریافتی</h2>
      <div class="flex gap-2 items-center">
        <label class="text-sm">تعداد:</label>
        <input v-model.number="count" type="number" min="1" max="100" class="input input-bordered input-sm w-24" />
        <button class="btn btn-primary btn-sm" :class="{ loading: loading }" :disabled="isSandbox" @click="load">دریافت</button>
      </div>
      <div v-if="error" class="text-sm text-error">{{ error }}</div>
      <pre v-if="data" class="text-xs bg-base-200/40 p-4 rounded-xl overflow-auto max-h-[32rem]" dir="ltr">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SmsApiResult, SmsProviderStatus } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, extractApiError } = useApi()
const count = ref(50)
const loading = ref(false)
const isSandbox = ref(false)
const error = ref('')
const data = ref<SmsApiResult | null>(null)

onMounted(async () => {
  const st = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  isSandbox.value = st.is_sandbox
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = await apiFetch<SmsApiResult>('/admin/sms/receive/latest/', { query: { count: count.value } })
  } catch (e: unknown) {
    error.value = extractApiError(e, 'خطا در دریافت')
  } finally {
    loading.value = false
  }
}
</script>
