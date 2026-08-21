<template>
  <div class="max-w-lg mx-auto bg-base-100 p-6 sm:p-8 rounded-3xl border border-base-200 text-right shadow-sm">
    <h2 class="text-xl font-bold mb-1">ورود / ثبت‌نام</h2>
    <p class="text-sm text-base-content/60 mb-5">برای ادامه‌ی خرید وارد شوید یا حساب بسازید.</p>

    <div class="grid grid-cols-2 gap-1 p-1 rounded-2xl bg-base-200/70 mb-6" role="tablist">
      <button
        type="button"
        role="tab"
        :aria-selected="mode === 'login'"
        class="btn btn-sm h-10 rounded-xl border-0 font-bold transition-all"
        :class="mode === 'login' ? 'btn-primary' : 'btn-ghost text-base-content/60'"
        @click="switchMode('login')"
      >
        ورود
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="mode === 'register'"
        class="btn btn-sm h-10 rounded-xl border-0 font-bold transition-all"
        :class="mode === 'register' ? 'btn-primary' : 'btn-ghost text-base-content/60'"
        @click="switchMode('register')"
      >
        ثبت‌نام
      </button>
    </div>

    <form class="space-y-5" novalidate @submit.prevent="submit">
      <CheckoutField id="auth_phone" label="شماره موبایل" required :error="fieldErrors.phone">
        <input
          id="auth_phone"
          v-model="form.phone"
          type="tel"
          inputmode="tel"
          maxlength="11"
          dir="ltr"
          class="input input-bordered w-full rounded-xl h-12 text-left"
          :class="{ 'input-error': fieldErrors.phone }"
          placeholder="09123456789"
          autocomplete="username"
          @input="form.phone = toEnDigits(form.phone).replace(/\D/g, '')"
        />
      </CheckoutField>

      <template v-if="mode === 'register'">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-5">
          <CheckoutField id="auth_first_name" label="نام" required :error="fieldErrors.first_name">
            <input
              id="auth_first_name"
              v-model="form.first_name"
              type="text"
              class="input input-bordered w-full rounded-xl h-12 text-right"
              :class="{ 'input-error': fieldErrors.first_name }"
              placeholder="مریم"
              autocomplete="given-name"
            />
          </CheckoutField>
          <CheckoutField id="auth_last_name" label="نام خانوادگی" required :error="fieldErrors.last_name">
            <input
              id="auth_last_name"
              v-model="form.last_name"
              type="text"
              class="input input-bordered w-full rounded-xl h-12 text-right"
              :class="{ 'input-error': fieldErrors.last_name }"
              placeholder="رضایی"
              autocomplete="family-name"
            />
          </CheckoutField>
        </div>
      </template>

      <CheckoutField
        id="auth_password"
        label="رمز عبور"
        required
        :hint="mode === 'register' ? 'حداقل ۴ کاراکتر' : ''"
        :error="fieldErrors.password"
      >
        <input
          id="auth_password"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          class="input input-bordered w-full rounded-xl h-12 text-right"
          :class="{ 'input-error': fieldErrors.password }"
          :autocomplete="mode === 'register' ? 'new-password' : 'current-password'"
        />
      </CheckoutField>

      <CheckoutField
        v-if="mode === 'register'"
        id="auth_password_confirm"
        label="تکرار رمز عبور"
        required
        :error="fieldErrors.password_confirm"
      >
        <input
          id="auth_password_confirm"
          v-model="form.password_confirm"
          :type="showPassword ? 'text' : 'password'"
          class="input input-bordered w-full rounded-xl h-12 text-right"
          :class="{ 'input-error': fieldErrors.password_confirm }"
          autocomplete="new-password"
        />
      </CheckoutField>

      <label class="flex items-center gap-2 text-xs text-base-content/60 cursor-pointer select-none">
        <input v-model="showPassword" type="checkbox" class="checkbox checkbox-xs" />
        نمایش رمز عبور
      </label>

      <div v-if="summary.length" class="rounded-2xl border border-error/30 bg-error/5 p-4" role="alert">
        <p class="text-sm font-bold text-error mb-1">
          {{ mode === 'login' ? 'ورود انجام نشد' : 'ثبت‌نام انجام نشد' }}
        </p>
        <ul class="space-y-1 text-xs text-error/90 leading-6 list-disc pr-4">
          <li v-for="message in summary" :key="message">{{ message }}</li>
        </ul>
      </div>

      <button type="submit" class="btn btn-primary w-full rounded-full h-12 font-bold" :disabled="loading">
        <span v-if="loading" class="loading loading-spinner loading-sm" />
        <span v-else>{{ mode === 'login' ? 'ورود و ادامه خرید' : 'ایجاد حساب و ادامه خرید' }}</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types'

const FIELD_LABELS: Record<string, string> = {
  phone: 'شماره موبایل',
  first_name: 'نام',
  last_name: 'نام خانوادگی',
  password: 'رمز عبور',
  password_confirm: 'تکرار رمز عبور',
}

const auth = useAuthStore()
const { apiFetch } = useApi()
const { fieldErrors, summary, clear: clearErrors, setField, setFromApi } = useFormErrors(FIELD_LABELS)

const mode = ref<'login' | 'register'>('login')
const form = reactive({ phone: '', first_name: '', last_name: '', password: '', password_confirm: '' })
const showPassword = ref(false)
const loading = ref(false)

const emit = defineEmits<{ authenticated: [] }>()

function switchMode(next: 'login' | 'register') {
  if (mode.value === next) return
  mode.value = next
  clearErrors()
}

function focusField(field: string) {
  nextTick(() => {
    const el = document.getElementById(`auth_${field}`)
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
  loading.value = true
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
    emit('authenticated')
  } catch (e: unknown) {
    const fallback = mode.value === 'login'
      ? 'شماره موبایل یا رمز عبور اشتباه است.'
      : 'ثبت‌نام انجام نشد. لطفاً اطلاعات وارد شده را بررسی کنید.'
    const firstBadField = setFromApi(e, fallback)
    if (firstBadField) focusField(firstBadField)
  } finally {
    loading.value = false
  }
}
</script>
