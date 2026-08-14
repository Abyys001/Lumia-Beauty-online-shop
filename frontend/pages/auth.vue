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
          @click="mode = 'login'"
        >
          ورود
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'register'"
          class="btn btn-sm h-11 rounded-xl border-0 font-bold transition-all"
          :class="mode === 'register' ? 'btn-primary shadow-md shadow-lumia-gold/20' : 'btn-ghost text-base-content/60'"
          @click="mode = 'register'"
        >
          ثبت‌نام
        </button>
      </div>

      <form class="space-y-5" @submit.prevent="submit">
        <div>
          <label class="block text-sm font-medium text-lumia-dark/80 mb-2">شماره موبایل</label>
          <input
            v-model="form.phone"
            type="tel"
            class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
            :class="{ 'input-error': fieldErrors.phone }"
            placeholder="۰۹۱۲۳۴۵۶۷۸۹"
            dir="ltr"
            inputmode="tel"
            autocomplete="username"
            required
            @input="form.phone = toEnDigits(form.phone)"
          />
          <p v-if="fieldErrors.phone" class="text-error text-xs mt-1.5 pr-1">{{ fieldErrors.phone }}</p>
        </div>

        <template v-if="mode === 'register'">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-lumia-dark/80 mb-2">نام</label>
              <input
                v-model="form.first_name"
                type="text"
                class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
                autocomplete="given-name"
              />
              <p v-if="fieldErrors.first_name" class="text-error text-xs mt-1.5 pr-1">{{ fieldErrors.first_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-lumia-dark/80 mb-2">نام خانوادگی</label>
              <input
                v-model="form.last_name"
                type="text"
                class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
                autocomplete="family-name"
              />
              <p v-if="fieldErrors.last_name" class="text-error text-xs mt-1.5 pr-1">{{ fieldErrors.last_name }}</p>
            </div>
          </div>
        </template>

        <div>
          <label class="block text-sm font-medium text-lumia-dark/80 mb-2">رمز عبور</label>
          <div class="relative">
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="input input-bordered w-full rounded-2xl h-12 text-base pl-12 focus:border-lumia-gold focus:outline-none transition-colors"
              :class="{ 'input-error': fieldErrors.password }"
              :placeholder="mode === 'register' ? 'حداقل ۴ کاراکتر' : ''"
              autocomplete="current-password"
              required
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
          <p v-if="fieldErrors.password" class="text-error text-xs mt-1.5 pr-1">{{ fieldErrors.password }}</p>
        </div>

        <div v-if="mode === 'register'">
          <label class="block text-sm font-medium text-lumia-dark/80 mb-2">تکرار رمز عبور</label>
          <input
            v-model="confirmPassword"
            :type="showPassword ? 'text' : 'password'"
            class="input input-bordered w-full rounded-2xl h-12 text-base focus:border-lumia-gold focus:outline-none transition-colors"
            :class="{ 'input-error': confirmError }"
            autocomplete="new-password"
            required
          />
          <p v-if="confirmError" class="text-error text-xs mt-1.5 pr-1">رمز عبور و تکرار آن یکسان نیستند</p>
        </div>

        <button
          type="submit"
          class="btn btn-primary w-full rounded-full h-12 text-base font-bold shadow-md shadow-lumia-gold/20 hover:shadow-lg transition-all"
          :disabled="submitting"
        >
          <span v-if="submitting" class="loading loading-spinner loading-sm" />
          <span v-else>{{ mode === 'login' ? 'ورود' : 'ایجاد حساب و ورود' }}</span>
        </button>

        <p v-if="error" class="text-error text-sm text-center bg-error/5 rounded-xl py-2.5 px-3">
          {{ error }}
        </p>
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

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { apiFetch } = useApi()

function toEnDigits(s: string): string {
  return s
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660))
}

const mode = ref<'login' | 'register'>('login')
const form = reactive({ phone: '', first_name: '', last_name: '', password: '' })
const confirmPassword = ref('')
const showPassword = ref(false)
const submitting = ref(false)
const error = ref('')
const fieldErrors = reactive<Record<string, string>>({})

const confirmError = computed(() => mode.value === 'register' && form.password !== confirmPassword.value)

function pickFieldError(data: Record<string, unknown>, field: string): string {
  const value = data?.[field]
  if (Array.isArray(value) && value.length) return String(value[0])
  if (typeof value === 'string' && value) return value
  return ''
}

function pickGeneralError(data: Record<string, unknown>): string {
  const detail = data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length) return String(detail[0])
  return ''
}

function resetErrors() {
  error.value = ''
  fieldErrors.phone = ''
  fieldErrors.password = ''
  fieldErrors.first_name = ''
  fieldErrors.last_name = ''
}

async function submit() {
  if (mode.value === 'register' && confirmError.value) return
  resetErrors()
  submitting.value = true
  try {
    const body = mode.value === 'login'
      ? { phone: form.phone, password: form.password }
      : {
          phone: form.phone,
          password: form.password,
          first_name: form.first_name,
          last_name: form.last_name,
        }
    const result = await apiFetch<{ access: string; refresh: string; user: User }>(
      mode.value === 'login' ? '/auth/login/' : '/auth/register/',
      { method: 'POST', body },
    )
    auth.setTokens(result.access, result.refresh, result.user)
    redirectAfterLogin(result.user)
  } catch (e: unknown) {
    const err = e as { data?: Record<string, unknown> }
    const data = err.data || {}
    const general = pickGeneralError(data)
    const phoneErr = pickFieldError(data, 'phone')
    const passwordErr = pickFieldError(data, 'password')
    if (phoneErr) fieldErrors.phone = phoneErr
    if (passwordErr) fieldErrors.password = passwordErr
    error.value = general
      || pickFieldError(data, 'first_name')
      || pickFieldError(data, 'last_name')
      || (mode.value === 'login' ? 'شماره موبایل یا رمز عبور اشتباه است' : 'خطا در ثبت‌نام')
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
