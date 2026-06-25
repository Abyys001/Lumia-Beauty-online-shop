<template>
  <div class="max-w-xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline">← داشبورد SMS</NuxtLink>

    <div v-if="isSandbox && isSmsIr" class="alert alert-warning text-sm">
      Sandbox: فقط قالب <strong dir="ltr">123456</strong> و پارامتر <strong dir="ltr">Code</strong>.
    </div>
    <div v-if="isIranPayamak" class="alert alert-info text-sm">
      IranPayamak: ارسال با <strong>Pattern</strong> — کد Pattern و شماره خط را در تنظیمات بررسی کنید.
    </div>

    <form class="bg-white rounded-2xl p-6 border border-base-200 space-y-4" @submit.prevent="send">
      <h2 class="font-bold text-lumia-dark">
        ارسال تست {{ isIranPayamak ? 'Pattern' : 'Verify' }}
      </h2>
      <div>
        <label class="label-text text-xs">شماره موبایل</label>
        <input v-model="phone" type="tel" class="input input-bordered w-full" dir="ltr" placeholder="09123456789" required />
      </div>
      <div>
        <label class="label-text text-xs">کد (اختیاری)</label>
        <input v-model="code" type="text" class="input input-bordered w-full" dir="ltr" placeholder="خالی = تولید خودکار" maxlength="8" />
      </div>
      <button type="submit" class="btn btn-primary btn-sm" :class="{ loading: sending }">ارسال تست</button>
    </form>

    <div v-if="result" class="rounded-2xl p-4 border text-sm space-y-2" :class="result.success ? 'border-success bg-success/5' : 'border-error bg-error/5'">
      <div><strong>نتیجه:</strong> {{ result.success ? 'موفق' : 'ناموفق' }}</div>
      <div v-if="result.error_hint"><strong>خطا:</strong> {{ result.error_hint }}</div>
      <div v-if="result.code_used"><strong>کد:</strong> <span dir="ltr">{{ result.code_used }}</span></div>
      <details>
        <summary class="cursor-pointer text-lumia-gold">Payload و پاسخ</summary>
        <pre class="text-xs mt-2 overflow-auto max-h-60" dir="ltr">{{ JSON.stringify({ payload: result.payload, data: result.data, status: result.status }, null, 2) }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SmsApiResult, SmsProviderStatus } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, extractApiError } = useApi()
const phone = ref('')
const code = ref('')
const sending = ref(false)
const result = ref<SmsApiResult | null>(null)
const status = ref<SmsProviderStatus | null>(null)

const isSandbox = computed(() => status.value?.is_sandbox ?? false)
const isSmsIr = computed(() => status.value?.runtime_provider === 'smsir')
const isIranPayamak = computed(() => status.value?.runtime_provider === 'iranpayamak')

onMounted(async () => {
  status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
})

async function send() {
  sending.value = true
  result.value = null
  try {
    result.value = await apiFetch<SmsApiResult>('/admin/sms/test-verify/', {
      method: 'POST',
      body: { phone: phone.value, code: code.value || undefined },
    })
  } catch (e: unknown) {
    const err = e as { data?: SmsApiResult }
    result.value = err.data || { success: false, error_hint: extractApiError(e, 'خطا در ارسال') }
  } finally {
    sending.value = false
  }
}
</script>
