<template>
  <div class="max-w-2xl space-y-6">
    <p class="text-sm text-lumia-dark/60">
      مدت اعتبار نشست‌ها، رفتار «مرا به خاطر بسپار» و شماره‌هایی که به‌صورت خودکار ادمین می‌شوند.
    </p>

    <div v-if="loading" class="bg-white rounded-2xl border border-base-200 p-8 text-center text-lumia-dark/40">
      در حال بارگذاری...
    </div>

    <template v-else>
      <div v-if="error" class="alert alert-error text-sm py-2 rounded-xl">{{ error }}</div>
      <div v-if="success" class="alert alert-success text-sm py-2 rounded-xl">{{ success }}</div>

      <section class="bg-white rounded-2xl border border-base-200 shadow-sm p-5 space-y-4">
        <h2 class="font-bold text-lumia-dark">مرا به خاطر بسپار</h2>
        <label class="flex items-start gap-3 cursor-pointer">
          <input v-model="form.remember_device_default" type="checkbox" class="checkbox checkbox-sm mt-0.5" />
          <span>
            <span class="block text-sm font-medium">تیک «مرا به خاطر بسپار» از ابتدا زده باشد</span>
            <span class="block text-xs text-lumia-dark/50 mt-0.5">
              در فرم ورود و ثبت‌نام. مشتری همیشه می‌تواند آن را بردارد.
            </span>
          </span>
        </label>
        <label class="form-control max-w-xs">
          <span class="label-text text-xs mb-1">مدت اعتبار دستگاه به‌خاطر سپرده‌شده (روز)</span>
          <input v-model.number="form.trusted_device_lifetime_days" type="number" min="1" max="3650" class="input input-bordered input-sm" dir="ltr" />
          <span class="text-xs text-lumia-dark/50 mt-1">هر ورود خودکار این مهلت را از نو تمدید می‌کند.</span>
        </label>
      </section>

      <section class="bg-white rounded-2xl border border-base-200 shadow-sm p-5 space-y-4">
        <h2 class="font-bold text-lumia-dark">نشست‌ها</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label class="form-control">
            <span class="label-text text-xs mb-1">عمر Access Token (دقیقه)</span>
            <input v-model.number="form.access_token_lifetime_minutes" type="number" min="1" class="input input-bordered input-sm" dir="ltr" />
          </label>
          <label class="form-control">
            <span class="label-text text-xs mb-1">عمر Refresh Token (روز)</span>
            <input v-model.number="form.refresh_token_lifetime_days" type="number" min="1" class="input input-bordered input-sm" dir="ltr" />
          </label>
        </div>
      </section>

      <section class="bg-white rounded-2xl border border-base-200 shadow-sm p-5 space-y-4">
        <h2 class="font-bold text-lumia-dark">شماره‌های ادمین</h2>
        <div v-if="!isSuperuser" class="alert alert-warning text-sm py-2 rounded-xl">
          فقط مدیر ارشد می‌تواند این بخش را تغییر دهد.
        </div>
        <template v-else>
          <p class="text-xs text-lumia-dark/50 leading-relaxed">
            هر شماره در این فهرست، در ورود یا ثبت‌نام به‌صورت خودکار مدیر ارشد می‌شود — حتی اگر
            دسترسی‌اش را در صفحه‌ی کاربران برداشته باشید.
          </p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="phone in form.admin_phones"
              :key="phone"
              class="badge badge-lg gap-2 font-mono"
            >
              {{ phone }}
              <button class="text-error" @click="removePhone(phone)">✕</button>
            </span>
            <span v-if="!form.admin_phones.length" class="text-sm text-lumia-dark/40">فهرست خالی است.</span>
          </div>
          <div class="flex gap-2">
            <input
              v-model="newPhone"
              class="input input-bordered input-sm font-mono flex-1 max-w-xs"
              dir="ltr"
              placeholder="09123456789"
              @keydown.enter.prevent="addPhone"
            />
            <button class="btn btn-sm" @click="addPhone">افزودن</button>
          </div>
          <label class="form-control max-w-xs border-t pt-4">
            <span class="label-text text-xs mb-1">شماره‌ی bypass (ورود با هر رمزی)</span>
            <input v-model="form.admin_bypass_phone" class="input input-bordered input-sm font-mono" dir="ltr" placeholder="خالی بگذارید" />
            <span class="text-xs text-error/80 mt-1">در محیط واقعی این را خالی بگذارید.</span>
          </label>
        </template>
      </section>

      <button class="btn btn-primary btn-sm" :disabled="saving" @click="save">
        <span v-if="saving" class="loading loading-spinner loading-sm" />
        <span v-else>ذخیره تنظیمات</span>
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

interface AuthSettings {
  access_token_lifetime_minutes: number
  refresh_token_lifetime_days: number
  rotate_refresh_tokens: boolean
  admin_bypass_phone: string
  admin_phones: string[]
  trusted_device_lifetime_days: number
  remember_device_default: boolean
}

const { apiFetch, extractApiError } = useApi()
const auth = useAuthStore()
const isSuperuser = computed(() => !!auth.user?.is_superuser)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const newPhone = ref('')

const form = reactive<AuthSettings>({
  access_token_lifetime_minutes: 15,
  refresh_token_lifetime_days: 90,
  rotate_refresh_tokens: true,
  admin_bypass_phone: '',
  admin_phones: [],
  trusted_device_lifetime_days: 180,
  remember_device_default: true,
})

function addPhone() {
  const phone = toEnDigits(newPhone.value).replace(/\D/g, '')
  if (!/^09\d{9}$/.test(phone)) {
    error.value = 'شماره باید ۱۱ رقم باشد و با ۰۹ شروع شود.'
    return
  }
  error.value = ''
  if (!form.admin_phones.includes(phone)) form.admin_phones.push(phone)
  newPhone.value = ''
}

function removePhone(phone: string) {
  form.admin_phones = form.admin_phones.filter(p => p !== phone)
}

async function load() {
  loading.value = true
  try {
    Object.assign(form, await apiFetch<AuthSettings>('/admin/auth/settings/'))
  } catch (e) {
    error.value = extractApiError(e, 'بارگذاری تنظیمات انجام نشد.')
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    // The server drops the privileged keys for non-superusers, so sending the
    // whole form is safe and keeps this page free of role branching.
    Object.assign(form, await apiFetch<AuthSettings>('/admin/auth/settings/', {
      method: 'PATCH',
      body: { ...form },
    }))
    success.value = 'تنظیمات ذخیره شد.'
  } catch (e) {
    error.value = extractApiError(e, 'ذخیره تنظیمات انجام نشد.')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
