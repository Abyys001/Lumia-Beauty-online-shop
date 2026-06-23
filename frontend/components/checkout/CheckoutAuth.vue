<template>
  <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm">
    <h2 class="text-xl font-bold mb-4">ورود سریع با موبایل</h2>

    <form v-if="step === 'phone'" @submit.prevent="requestOtp">
      <input
        v-model="phone"
        type="tel"
        class="input input-bordered w-full rounded-xl mb-4 text-right"
        placeholder="۰۹۱۲۳۴۵۶۷۸۹"
        dir="ltr"
        required
      />
      <button type="submit" class="btn btn-primary w-full rounded-full" :disabled="loading">
        <span v-if="loading" class="loading loading-spinner loading-sm" />
        <span v-else>دریافت کد تأیید</span>
      </button>
    </form>

    <form v-else @submit.prevent="verifyOtp">
      <p class="text-sm text-base-content/60 mb-4">کد ارسال‌شده به {{ phone }} را وارد کنید</p>
      <input
        v-model="code"
        type="text"
        class="input input-bordered w-full rounded-xl mb-4 text-center tracking-widest"
        maxlength="6"
        dir="ltr"
        required
      />
      <p v-if="debugCode" class="text-xs text-warning mb-2">کد تست: {{ debugCode }}</p>
      <button type="submit" class="btn btn-primary w-full rounded-full mb-2" :disabled="loading">
        تأیید و ادامه خرید
      </button>
      <button type="button" class="btn btn-ghost btn-sm w-full" @click="step = 'phone'">تغییر شماره</button>
    </form>

    <p v-if="error" class="text-error text-sm mt-3 text-center">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types'

const auth = useAuthStore()
const { apiFetch } = useApi()

const step = ref<'phone' | 'code'>('phone')
const phone = ref('')
const code = ref('')
const loading = ref(false)
const error = ref('')
const debugCode = ref('')

const emit = defineEmits<{ authenticated: [] }>()

async function requestOtp() {
  loading.value = true
  error.value = ''
  try {
    const result = await apiFetch<{ detail: string; debug_code?: string }>('/auth/otp/request/', {
      method: 'POST',
      body: { phone: phone.value },
    })
    debugCode.value = result.debug_code || ''
    step.value = 'code'
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ارسال کد'
  } finally {
    loading.value = false
  }
}

async function verifyOtp() {
  loading.value = true
  error.value = ''
  try {
    const result = await apiFetch<{ access: string; refresh: string; user: User }>('/auth/otp/verify/', {
      method: 'POST',
      body: { phone: phone.value, code: code.value },
    })
    auth.setTokens(result.access, result.refresh, result.user)
    emit('authenticated')
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'کد نامعتبر'
  } finally {
    loading.value = false
  }
}
</script>
