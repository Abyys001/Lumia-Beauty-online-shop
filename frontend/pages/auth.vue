<template>
  <div class="w-full max-w-md mx-auto">
    <div class="sticky top-16 z-40 -mx-1 px-1 pb-3 bg-gradient-to-b from-base-100 via-base-100/95 to-transparent">
      <PageBack to="/" label="بازگشت به خانه" />
    </div>

    <!-- Welcome -->
    <div class="text-center mb-8 animate-fade-in">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-lumia-gold/15 border border-lumia-gold/25 mb-4 shadow-sm">
        <img src="/logo.svg" alt="" class="w-9 h-9 object-contain" aria-hidden="true" />
      </div>
      <p class="text-xs font-semibold tracking-wide text-lumia-gold uppercase mb-2">خوش آمدید</p>
      <h1 class="text-2xl sm:text-3xl font-bold text-lumia-dark leading-snug">
        {{ step === 'phone' ? 'به لومیا بیوتی خوش آمدید' : 'کد تأیید را وارد کنید' }}
      </h1>
      <p class="text-sm text-base-content/60 mt-3 leading-relaxed max-w-xs mx-auto">
        <template v-if="step === 'phone'">
          با شماره موبایل خود وارد شوید یا ثبت‌نام کنید — سریع، امن و بدون رمز عبور.
        </template>
        <template v-else>
          پیامک حاوی کد ۶ رقمی به شماره
          <span class="font-mono text-lumia-dark/80" dir="ltr">{{ phone }}</span>
          ارسال شد.
        </template>
      </p>
    </div>

    <!-- Card -->
    <div class="bg-white/90 backdrop-blur-sm rounded-3xl border border-lumia-cream shadow-lg shadow-lumia-dark/5 p-6 sm:p-8">
      <form v-if="step === 'phone'" class="space-y-5" @submit.prevent="requestOtp">
        <div>
          <label class="block text-sm font-medium text-lumia-dark/80 mb-2">شماره موبایل</label>
          <input
            v-model="phone"
            type="tel"
            class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
            placeholder="۰۹۱۲۳۴۵۶۷۸۹"
            dir="ltr"
            inputmode="tel"
            autocomplete="tel"
            required
            @input="phone = toEnDigits(phone)"
          />
        </div>
        <button
          type="submit"
          class="btn btn-primary w-full rounded-full h-12 text-base font-bold shadow-md shadow-lumia-gold/20 hover:shadow-lg transition-all"
          :disabled="loading"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          <span v-else>دریافت کد تأیید</span>
        </button>
      </form>

      <form v-else class="space-y-5" @submit.prevent="verifyOtp">
        <!-- OTP Timer -->
        <div class="flex flex-col items-center py-2">
          <div class="relative w-28 h-28">
            <svg class="w-full h-full -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
              <defs>
                <linearGradient id="otp-ring-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#c9a96e" />
                  <stop offset="100%" stop-color="#8b6f5c" />
                </linearGradient>
              </defs>
              <circle cx="60" cy="60" r="52" fill="none" stroke="currentColor" stroke-width="6" class="text-base-200" />
              <circle
                cx="60"
                cy="60"
                r="52"
                fill="none"
                stroke="url(#otp-ring-gradient)"
                stroke-width="6"
                stroke-linecap="round"
                :stroke-dasharray="ringCircumference"
                :stroke-dashoffset="ringOffset"
                class="transition-[stroke-dashoffset] duration-1000 ease-linear"
              />
            </svg>
            <div class="absolute inset-0 flex flex-col items-center justify-center">
              <span
                class="text-2xl font-bold tabular-nums tracking-tight"
                :class="remainingSeconds > 30 ? 'text-lumia-dark' : remainingSeconds > 0 ? 'text-warning' : 'text-error'"
                dir="ltr"
              >
                {{ formattedTime }}
              </span>
              <span class="text-[10px] text-base-content/50 mt-0.5">اعتبار کد</span>
            </div>
          </div>
          <p class="text-xs text-center text-base-content/55 mt-4 leading-relaxed max-w-[240px]">
            <template v-if="remainingSeconds > 0">
              کد پیامکی تا
              <strong class="text-lumia-dark/80">{{ formattedTime }}</strong>
              معتبر است — همین کد را وارد کنید.
            </template>
            <template v-else>
              زمان اعتبار کد به پایان رسید. می‌توانید کد جدید دریافت کنید.
            </template>
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-lumia-dark/80 mb-2 text-center">کد ۶ رقمی</label>
          <input
            ref="codeInputRef"
            v-model="code"
            type="text"
            class="input input-bordered w-full rounded-2xl h-14 text-center tracking-[0.35em] text-xl font-mono focus:border-lumia-gold focus:outline-none"
            placeholder="• • • • • •"
            maxlength="6"
            dir="ltr"
            inputmode="numeric"
            autocomplete="one-time-code"
            required
            :disabled="remainingSeconds === 0"
            @input="code = toEnDigits(code).replace(/\D/g, '').slice(0, 6)"
          />
        </div>

        <p v-if="simulated && debugCode" class="text-xs text-warning text-center bg-warning/10 rounded-xl py-2 px-3">
          حالت تست: کد
          <strong dir="ltr" class="font-mono">{{ debugCode }}</strong>
        </p>

        <button
          type="submit"
          class="btn btn-primary w-full rounded-full h-12 font-bold"
          :disabled="loading || remainingSeconds === 0 || code.length < 6"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          <span v-else>تأیید و ورود</span>
        </button>

        <div class="flex flex-col gap-2 pt-1">
          <button
            type="button"
            class="btn btn-outline btn-sm rounded-full border-lumia-gold/40 text-lumia-gold hover:bg-lumia-gold/10"
            :disabled="remainingSeconds > 0 || resending"
            @click="resendOtp"
          >
            <span v-if="resending" class="loading loading-spinner loading-xs" />
            <span v-else-if="remainingSeconds > 0">ارسال مجدد ({{ formattedTime }})</span>
            <span v-else>دریافت کد جدید</span>
          </button>
          <button type="button" class="btn btn-ghost btn-sm rounded-full text-base-content/60" @click="goBackToPhone">
            تغییر شماره موبایل
          </button>
        </div>
      </form>

      <p v-if="error" class="text-error text-sm mt-5 text-center bg-error/5 rounded-xl py-2.5 px-3">
        {{ error }}
      </p>
    </div>

    <p v-if="step === 'phone'" class="text-center text-xs text-base-content/45 mt-6 leading-relaxed">
      با ورود، شرایط استفاده و حریم خصوصی لومیا بیوتی را می‌پذیرید.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types'

definePageMeta({ layout: 'auth' })

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { apiFetch } = useApi()

const OTP_DEFAULT_SECONDS = 120

function toEnDigits(s: string): string {
  return s
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660))
}

function toFaDigits(n: number | string): string {
  return String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[Number(d)])
}

const step = ref<'phone' | 'code'>('phone')
const phone = ref('')
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const error = ref('')
const debugCode = ref('')
const simulated = ref(false)
const codeInputRef = ref<HTMLInputElement | null>(null)

const totalSeconds = ref(OTP_DEFAULT_SECONDS)
const remainingSeconds = ref(0)
let timerId: ReturnType<typeof setInterval> | null = null

const ringCircumference = 2 * Math.PI * 52
const ringOffset = computed(() => {
  if (totalSeconds.value <= 0) return ringCircumference
  const progress = remainingSeconds.value / totalSeconds.value
  return ringCircumference * (1 - progress)
})

const formattedTime = computed(() => {
  const m = Math.floor(remainingSeconds.value / 60)
  const s = remainingSeconds.value % 60
  return `${toFaDigits(m)}:${toFaDigits(String(s).padStart(2, '0'))}`
})

function clearTimer() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

function startTimer(seconds: number) {
  clearTimer()
  totalSeconds.value = seconds
  remainingSeconds.value = seconds
  timerId = setInterval(() => {
    if (remainingSeconds.value > 0) {
      remainingSeconds.value -= 1
    } else {
      clearTimer()
    }
  }, 1000)
}

function goBackToPhone() {
  clearTimer()
  remainingSeconds.value = 0
  step.value = 'phone'
  code.value = ''
  error.value = ''
  debugCode.value = ''
  simulated.value = false
}

async function requestOtp() {
  loading.value = true
  error.value = ''
  try {
    const result = await apiFetch<{
      detail?: string
      debug_code?: string
      simulated?: boolean
      expires_in?: number
      access?: string
      refresh?: string
      user?: User
    }>('/auth/otp/request/', {
      method: 'POST',
      body: { phone: phone.value },
    })
    if (result.access && result.refresh && result.user) {
      auth.setTokens(result.access, result.refresh, result.user)
      redirectAfterLogin(result.user)
      return
    }
    simulated.value = Boolean(result.simulated)
    debugCode.value = result.debug_code || ''
    if (debugCode.value) {
      code.value = debugCode.value
    } else {
      code.value = ''
    }
    step.value = 'code'
    startTimer(result.expires_in ?? OTP_DEFAULT_SECONDS)
    await nextTick()
    codeInputRef.value?.focus()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ارسال کد'
  } finally {
    loading.value = false
  }
}

async function resendOtp() {
  if (remainingSeconds.value > 0 || resending.value) return
  resending.value = true
  error.value = ''
  code.value = ''
  try {
    const result = await apiFetch<{ detail?: string; debug_code?: string; simulated?: boolean; expires_in?: number }>('/auth/otp/request/', {
      method: 'POST',
      body: { phone: phone.value },
    })
    simulated.value = Boolean(result.simulated)
    debugCode.value = result.debug_code || ''
    if (debugCode.value) {
      code.value = debugCode.value
    }
    startTimer(result.expires_in ?? OTP_DEFAULT_SECONDS)
    await nextTick()
    codeInputRef.value?.focus()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ارسال مجدد کد'
  } finally {
    resending.value = false
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
    clearTimer()
    auth.setTokens(result.access, result.refresh, result.user)
    redirectAfterLogin(result.user)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string; message?: string } }
    error.value = err.data?.detail || err.data?.message || 'کد نامعتبر'
  } finally {
    loading.value = false
  }
}

function redirectAfterLogin(user: User) {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect && redirect.startsWith('/') && !redirect.startsWith('//')) {
    if (!redirect.startsWith('/admin') || user.is_staff) {
      router.push(redirect)
      return
    }
  }
  router.push(user.is_staff ? '/admin' : '/account')
}

onUnmounted(clearTimer)

useSeoMeta({
  title: 'ورود / ثبت‌نام | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
</style>
