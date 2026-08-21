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
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="input input-bordered w-full rounded-2xl h-12 text-base pl-12 focus:border-lumia-gold focus:outline-none transition-colors"
              :class="{ 'input-error': fieldErrors.password }"
              :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
            />
            <button
              type="button"
              class="absolute left-1 top-1/2 -translate-y-1/2 btn btn-ghost btn-xs text-base-content/50"
              aria-label="نمایش رمز عبور"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </CheckoutField>

        <CheckoutField
          v-if="mode === 'register'"
          id="password_confirm"
          label="تکرار رمز عبور"
          required
          :error="fieldErrors.password_confirm"
        >
          <input
            id="password_confirm"
            v-model="form.password_confirm"
            :type="showPassword ? 'text' : 'password'"
            class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
            :class="{ 'input-error': fieldErrors.password_confirm }"
            autocomplete="new-password"
          />
        </CheckoutField>

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
import type { User } from '~/types'

definePageMeta({ layout: 'auth' })

const FIELD_LABELS: Record<string, string> = {
  phone: 'شماره موبایل',
  first_name: 'نام',
  last_name: 'نام خانوادگی',
  password: 'رمز عبور',
  password_confirm: 'تکرار رمز عبور',
}

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { apiFetch } = useApi()
const { fieldErrors, summary, clear: clearErrors, setField, setFromApi } = useFormErrors(FIELD_LABELS)

const mode = ref<'login' | 'register'>('login')
const form = reactive({ phone: '', first_name: '', last_name: '', password: '', password_confirm: '' })
const showPassword = ref(false)
const submitting = ref(false)

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
    const body = mode.value === 'login'
      ? { phone: form.phone, password: form.password }
      : {
          phone: form.phone,
          password: form.password,
          first_name: form.first_name.trim(),
          last_name: form.last_name.trim(),
        }
    const result = await apiFetch<{ access: string; refresh: string; user: User }>(
      mode.value === 'login' ? '/auth/login/' : '/auth/register/',
      { method: 'POST', body },
    )
    auth.setTokens(result.access, result.refresh, result.user)
    redirectAfterLogin(result.user)
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
