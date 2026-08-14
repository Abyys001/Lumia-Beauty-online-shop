<template>
  <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm">
    <h2 class="text-xl font-bold mb-1">ورود / ثبت‌نام</h2>
    <p class="text-sm text-base-content/60 mb-4">برای ادامه‌ی خرید وارد شوید یا حساب بسازید.</p>

    <div class="grid grid-cols-2 gap-1 p-1 rounded-xl bg-base-200/70 mb-4" role="tablist">
      <button
        type="button"
        role="tab"
        :aria-selected="mode === 'login'"
        class="btn btn-sm h-9 rounded-lg border-0 font-bold transition-all"
        :class="mode === 'login' ? 'btn-primary' : 'btn-ghost text-base-content/60'"
        @click="mode = 'login'"
      >
        ورود
      </button>
      <button
        type="button"
        role="tab"
        :aria-selected="mode === 'register'"
        class="btn btn-sm h-9 rounded-lg border-0 font-bold transition-all"
        :class="mode === 'register' ? 'btn-primary' : 'btn-ghost text-base-content/60'"
        @click="mode = 'register'"
      >
        ثبت‌نام
      </button>
    </div>

    <form @submit.prevent="submit">
      <input
        v-model="form.phone"
        type="tel"
        class="input input-bordered w-full rounded-xl mb-3 text-right"
        :class="{ 'input-error': fieldErrors.phone }"
        placeholder="۰۹۱۲۳۴۵۶۷۸۹"
        dir="ltr"
        autocomplete="username"
        required
        @input="form.phone = toEnDigits(form.phone)"
      />
      <p v-if="fieldErrors.phone" class="text-error text-xs -mt-2 mb-2 pr-1">{{ fieldErrors.phone }}</p>

      <template v-if="mode === 'register'">
        <div class="grid grid-cols-2 gap-3 mb-3">
          <input
            v-model="form.first_name"
            type="text"
            class="input input-bordered w-full rounded-xl text-right"
            placeholder="نام"
            autocomplete="given-name"
          />
          <input
            v-model="form.last_name"
            type="text"
            class="input input-bordered w-full rounded-xl text-right"
            placeholder="نام خانوادگی"
            autocomplete="family-name"
          />
        </div>
      </template>

      <input
        v-model="form.password"
        :type="showPassword ? 'text' : 'password'"
        class="input input-bordered w-full rounded-xl mb-1 text-right"
        :class="{ 'input-error': fieldErrors.password }"
        :placeholder="mode === 'register' ? 'رمز عبور (حداقل ۴ کاراکتر)' : 'رمز عبور'"
        autocomplete="current-password"
        required
      />
      <p v-if="fieldErrors.password" class="text-error text-xs mb-1 pr-1">{{ fieldErrors.password }}</p>
      <label class="flex items-center gap-2 text-xs text-base-content/60 mb-3 cursor-pointer select-none">
        <input v-model="showPassword" type="checkbox" class="checkbox checkbox-xs" />
        نمایش رمز عبور
      </label>

      <p v-if="error" class="text-error text-sm mb-3 text-center">{{ error }}</p>

      <button type="submit" class="btn btn-primary w-full rounded-full" :disabled="loading">
        <span v-if="loading" class="loading loading-spinner loading-sm" />
        <span v-else>{{ mode === 'login' ? 'ورود و ادامه خرید' : 'ایجاد حساب و ادامه خرید' }}</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { User } from '~/types'

const auth = useAuthStore()
const { apiFetch } = useApi()

function toEnDigits(s: string): string {
  return s
    .replace(/[۰-۹]/g, d => String(d.charCodeAt(0) - 0x06F0))
    .replace(/[٠-٩]/g, d => String(d.charCodeAt(0) - 0x0660))
}

const mode = ref<'login' | 'register'>('login')
const form = reactive({ phone: '', first_name: '', last_name: '', password: '' })
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const fieldErrors = reactive<Record<string, string>>({})

const emit = defineEmits<{ authenticated: [] }>()

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

async function submit() {
  loading.value = true
  error.value = ''
  fieldErrors.phone = ''
  fieldErrors.password = ''
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
    emit('authenticated')
  } catch (e: unknown) {
    const err = e as { data?: Record<string, unknown> }
    const data = err.data || {}
    fieldErrors.phone = pickFieldError(data, 'phone')
    fieldErrors.password = pickFieldError(data, 'password')
    error.value = pickGeneralError(data)
      || fieldErrors.phone
      || fieldErrors.password
      || (mode.value === 'login' ? 'شماره موبایل یا رمز عبور اشتباه است' : 'خطا در ثبت‌نام')
  } finally {
    loading.value = false
  }
}
</script>
