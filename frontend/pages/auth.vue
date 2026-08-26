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
        به لومیا بیوتی خوش آمدید
      </h1>
      <p class="text-sm text-base-content/60 mt-3 leading-relaxed max-w-xs mx-auto">
        با شماره موبایل و رمز عبور خود وارد شوید یا یک حساب جدید بسازید.
      </p>
    </div>

    <!-- Card -->
    <div class="bg-white/90 backdrop-blur-sm rounded-3xl border border-lumia-cream shadow-lg shadow-lumia-dark/5 p-6 sm:p-8">
      <!-- Tabs -->
      <div class="grid grid-cols-2 gap-1 p-1 rounded-2xl bg-base-200/70 mb-6" role="tablist">
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'login'"
          class="btn btn-sm h-11 rounded-xl border-0 font-bold transition-all"
          :class="mode === 'login' ? 'btn-primary shadow-md shadow-lumia-gold/20' : 'btn-ghost text-base-content/60'"
          @click="switchMode('login')"
        >
          ورود
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'register'"
          class="btn btn-sm h-11 rounded-xl border-0 font-bold transition-all"
          :class="mode === 'register' ? 'btn-primary shadow-md shadow-lumia-gold/20' : 'btn-ghost text-base-content/60'"
          @click="switchMode('register')"
        >
          ثبت‌نام
        </button>
      </div>

      <form class="space-y-5" novalidate @submit.prevent="submit">
        <CheckoutField id="phone" label="شماره موبایل" required :error="fieldErrors.phone">
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            class="input input-bordered w-full rounded-2xl h-12 text-base text-left focus:border-lumia-gold focus:outline-none transition-colors"
            :class="{ 'input-error': fieldErrors.phone }"
            placeholder="09123456789"
            dir="ltr"
            inputmode="tel"
            maxlength="11"
            autocomplete="username"
            @input="form.phone = toEnDigits(form.phone).replace(/\D/g, '')"
          />
        </CheckoutField>

        <template v-if="mode === 'register'">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-5">
            <CheckoutField id="first_name" label="نام" required :error="fieldErrors.first_name">
              <input
                id="first_name"
                v-model="form.first_name"
                type="text"
                class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
                :class="{ 'input-error': fieldErrors.first_name }"
                placeholder="مریم"
                autocomplete="given-name"
              />
            </CheckoutField>
            <CheckoutField id="last_name" label="نام خانوادگی" required :error="fieldErrors.last_name">
              <input
                id="last_name"
                v-model="form.last_name"
                type="text"
                class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
                :class="{ 'input-error': fieldErrors.last_name }"
                placeholder="رضایی"
                autocomplete="family-name"
              />
            </CheckoutField>
          </div>
        </template>

        <CheckoutField
          id="password"
          label="رمز عبور"
          required
          :hint="mode === 'register' ? 'حداقل ۴ کاراکتر' : ''"
          :error="fieldErrors.password"
        >
          <UiPasswordInput
            id="password"
            v-model="form.password"
            :input-class="`rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors ${fieldErrors.password ? 'input-error' : ''}`"
            :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
          />
        </CheckoutField>

        <CheckoutField
          v-if="mode === 'register'"
          id="password_confirm"
          label="تکرار رمز عبور"
          required
          :error="fieldErrors.password_confirm"
        >
          <UiPasswordInput
            id="password_confirm"
            v-model="form.password_confirm"
            :input-class="`rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors ${fieldErrors.password_confirm ? 'input-error' : ''}`"
            autocomplete="new-password"
          />
        </CheckoutField>

        <label class="flex items-start gap-3 cursor-pointer rounded-2xl border border-lumia-cream bg-base-200/40 p-4 transition-colors hover:border-lumia-gold/40">
          <input
            v-model="form.remember_device"
            type="checkbox"
            class="checkbox checkbox-sm checkbox-primary mt-0.5 flex-shrink-0"
          />
          <span class="text-right">
            <span class="block text-sm font-bold text-lumia-dark">این دستگاه را به خاطر بسپار</span>
            <span class="block text-xs text-base-content/55 mt-1 leading-relaxed">
              دفعه‌ی بعد بدون وارد کردن رمز عبور وارد می‌شوید.
              <template v-if="rememberDays">تا {{ rememberDaysLabel }} روز روی همین مرورگر فعال است.</template>
              روی دستگاه‌های عمومی این گزینه را بردارید.
            </span>
          </span>
        </label>

        <div v-if="summary.length" class="rounded-2xl border border-error/30 bg-error/5 p-4 text-right" role="alert">
          <p class="text-sm font-bold text-error mb-1">
            {{ mode === 'login' ? 'ورود انجام نشد' : 'ثبت‌نام انجام نشد' }}
          </p>
          <ul class="space-y-1 text-xs text-error/90 leading-6 list-disc pr-4">
            <li v-for="message in summary" :key="message">{{ message }}</li>
          </ul>
        </div>

        <button
          type="submit"
          class="btn btn-primary w-full rounded-full h-12 text-base font-bold shadow-md shadow-lumia-gold/20 hover:shadow-lg transition-all"
          :disabled="submitting"
        >
          <span v-if="submitting" class="loading loading-spinner loading-sm" />
          <span v-else>{{ mode === 'login' ? 'ورود' : 'ایجاد حساب و ورود' }}</span>
        </button>
      </form>
    </div>

    <p class="text-center text-xs text-base-content/45 mt-6 leading-relaxed">
      با ورود، شرایط استفاده و حریم خصوصی لومیا بیوتی را می‌پذیرید.
    </p>
  </div>
</template>

<script setup lang="ts">
import type { TrustedDeviceGrant, User } from '~/types'

definePageMeta({ layout: 'auth' })

const FIELD_LABELS: Record<string, string> = {
  phone: 'شماره موبایل',
  first_name: 'نام',
  last_name: 'نام خانوادگی',
  password: 'رمز عبور',
  password_confirm: 'تکرار رمز عبور',
}

const auth = useAuthStore()
const route = useRoute()
const { apiFetch } = useApi()
const { fieldErrors, summary, clear: clearErrors, setField, setFromApi } = useFormErrors(FIELD_LABELS)

const mode = ref<'login' | 'register'>('login')
const form = reactive({
  phone: '', first_name: '', last_name: '', password: '', password_confirm: '',
  remember_device: true,
})
const submitting = ref(false)
const rememberDays = ref(0)
const rememberDaysLabel = computed(() => new Intl.NumberFormat('fa-IR').format(rememberDays.value))

// The seller controls the default tick and the window from /admin/settings; a
// failed lookup just leaves the checkbox on, which is the behaviour we want.
onMounted(async () => {
  // A remembered device is signed in by the auth plugin before this runs, so
  // landing on the sign-in form means there is nothing left to sign in to.
  if (auth.isAuthenticated && auth.user) {
    await redirectAfterLogin(auth.user)
    return
  }
  try {
    const policy = await apiFetch<{ remember_device_default: boolean; trusted_device_lifetime_days: number }>(
      '/auth/device/policy/',
    )
    form.remember_device = policy.remember_device_default
    rememberDays.value = policy.trusted_device_lifetime_days
  } catch {
    // Keep the pre-ticked default.
  }
})

function switchMode(next: 'login' | 'register') {
  if (mode.value === next) return
  mode.value = next
  clearErrors()
}

function focusField(field: string) {
  nextTick(() => {
    const el = document.getElementById(field)
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    ;(el as HTMLElement | null)?.focus?.({ preventScroll: true })
  })
}

function validate(): boolean {
  clearErrors()

  if (!form.phone) setField('phone', 'شماره موبایل الزامی است.')
  else if (!/^09\d{9}$/.test(form.phone))
    setField('phone', 'شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود. مثال: ۰۹۱۲۳۴۵۶۷۸۹')

  if (!form.password) setField('password', 'رمز عبور الزامی است.')
  else if (mode.value === 'register' && form.password.length < 4)
    setField('password', 'رمز عبور باید حداقل ۴ کاراکتر باشد.')

  if (mode.value === 'register') {
    if (!form.first_name.trim()) setField('first_name', 'نام الزامی است.')
    if (!form.last_name.trim()) setField('last_name', 'نام خانوادگی الزامی است.')
    if (!form.password_confirm) setField('password_confirm', 'تکرار رمز عبور الزامی است.')
    else if (form.password && form.password !== form.password_confirm)
      setField('password_confirm', 'رمز عبور و تکرار آن یکسان نیستند.')
  }

  const firstBadField = Object.keys(FIELD_LABELS).find(field => fieldErrors[field])
  if (firstBadField) {
    focusField(firstBadField)
    return false
  }
  return true
}

async function submit() {
  if (!validate()) return
  submitting.value = true
  try {
    const shared = {
      phone: form.phone,
      password: form.password,
      remember_device: form.remember_device,
      device_name: describeThisDevice(),
    }
    const body = mode.value === 'login'
      ? shared
      : { ...shared, first_name: form.first_name.trim(), last_name: form.last_name.trim() }
    const result = await apiFetch<{
      access: string
      refresh: string
      user: User
      device: TrustedDeviceGrant | null
    }>(
      mode.value === 'login' ? '/auth/login/' : '/auth/register/',
      { method: 'POST', body },
    )
    auth.setTokens(result.access, result.refresh, result.user, result.device)
    await redirectAfterLogin(result.user)
  } catch (e: unknown) {
    const fallback = mode.value === 'login'
      ? 'شماره موبایل یا رمز عبور اشتباه است.'
      : 'ثبت‌نام انجام نشد. لطفاً اطلاعات وارد شده را بررسی کنید.'
    const firstBadField = setFromApi(e, fallback)
    if (firstBadField) focusField(firstBadField)
  } finally {
    submitting.value = false
  }
}

async function redirectAfterLogin(user: User) {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect && redirect.startsWith('/') && !redirect.startsWith('//')) {
    if (!redirect.startsWith('/admin') || user.is_staff) {
      await navigateTo(redirect)
      return
    }
  }
  await navigateTo(user.is_staff ? '/admin' : '/account')
}

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
