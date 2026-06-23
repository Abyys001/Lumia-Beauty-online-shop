<template>
  <div class="container-lumia py-8 max-w-lg mx-auto">
    <h1 class="section-title text-center">ورود / ثبت‌نام</h1>
    <p class="section-subtitle text-center">با شماره موبایل وارد شوید</p>

    <div class="card-lumia p-6 mt-6">
      <form v-if="step === 'phone'" @submit.prevent="requestOtp">
        <label class="label">
          <span class="label-text">شماره موبایل</span>
        </label>
        <input
          v-model="phone"
          type="tel"
          class="input input-bordered w-full rounded-xl mb-4"
          placeholder="۰۹۱۲۳۴۵۶۷۸۹"
          dir="ltr"
          required
          @input="phone = toEnDigits(phone)"
        />
        <button type="submit" class="btn btn-primary w-full rounded-full" :disabled="loading">
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          <span v-else>دریافت کد تأیید</span>
        </button>
      </form>

      <form v-else @submit.prevent="verifyOtp">
        <p class="text-sm text-base-content/60 mb-4">
          کد ارسال شده به {{ phone }} را وارد کنید
        </p>
        <input
          v-model="code"
          type="text"
          class="input input-bordered w-full rounded-xl mb-4 text-center tracking-widest text-lg"
          placeholder="------"
          maxlength="6"
          dir="ltr"
          required
        />
        <p v-if="debugCode" class="text-xs text-warning mb-2">کد تست: {{ debugCode }}</p>
        <button type="submit" class="btn btn-primary w-full rounded-full mb-2" :disabled="loading">
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          <span v-else>تأیید و ورود</span>
        </button>
        <button type="button" class="btn btn-ghost btn-sm w-full" @click="step = 'phone'">
          تغییر شماره
        </button>
      </form>

      <p v-if="error" class="text-error text-sm mt-4 text-center">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types'

const auth = useAuthStore()
const router = useRouter()
const { apiFetch } = useApi()

function toEnDigits(s: string): string {
  return s
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660))
}

const step = ref<'phone' | 'code'>('phone')
const phone = ref('')
const code = ref('')
const loading = ref(false)
const error = ref('')
const debugCode = ref('')

async function requestOtp() {
  loading.value = true
  error.value = ''
  try {
    const result = await apiFetch<{ detail?: string; debug_code?: string; access?: string; refresh?: string; user?: User }>('/auth/otp/request/', {
      method: 'POST',
      body: { phone: phone.value },
    })
    if (result.access && result.refresh && result.user) {
      auth.setTokens(result.access, result.refresh, result.user)
      router.push(result.user.is_staff ? '/admin' : '/account')
      return
    }
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
    router.push(result.user.is_staff ? '/admin' : '/account')
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'کد نامعتبر'
  } finally {
    loading.value = false
  }
}

useSeoMeta({
  title: 'ورود / ثبت‌نام | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
