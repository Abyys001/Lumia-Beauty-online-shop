<template>
  <div class="max-w-2xl">
    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-5" @submit.prevent="save">
      <div class="pb-4 border-b border-base-200">
        <h2 class="font-bold text-lumia-dark">راه‌های ارتباطی پرداخت</h2>
        <p class="mt-1 text-xs text-lumia-dark/50">
          این چهار مورد دقیقاً همان دکمه‌هایی هستند که بعد از ثبت سفارش به مشتری نمایش داده می‌شوند تا کد خرید را برای شما بفرستد. هر کدام را خالی بگذارید، آن دکمه غیرفعال می‌شود.
        </p>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">شماره پیامک (SMS)</label>
        <input v-model="form.contact_sms_phone" class="input input-bordered w-full" dir="ltr" placeholder="09123456789" />
        <p class="text-xs text-lumia-dark/40 mt-1">مشتری با زدن دکمه، پیامک آماده به این شماره ارسال می‌کند.</p>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">شناسه تلگرام</label>
        <input v-model="form.contact_telegram" class="input input-bordered w-full" dir="ltr" placeholder="lumia_beauty" />
        <p class="text-xs text-lumia-dark/40 mt-1">بدون @ — لینک t.me/… ساخته می‌شود.</p>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">شماره واتس‌اپ</label>
        <input v-model="form.contact_whatsapp" class="input input-bordered w-full" dir="ltr" placeholder="989123456789" />
        <p class="text-xs text-lumia-dark/40 mt-1">با کد کشور و بدون + (۰۹۱۲… هم پذیرفته و به ۹۸۹۱۲… تبدیل می‌شود).</p>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">شناسه بله</label>
        <input v-model="form.contact_bale" class="input input-bordered w-full" dir="ltr" placeholder="lumia_beauty" />
        <p class="text-xs text-lumia-dark/40 mt-1">بدون @ — لینک bale.me/… ساخته می‌شود.</p>
      </div>

      <div class="rounded-xl bg-lumia-cream/30 border border-lumia-cream p-4 text-sm text-lumia-dark/70 space-y-1">
        <p class="font-bold">پیش‌نمایش دکمه‌های مشتری:</p>
        <ul class="space-y-1">
          <li v-for="ch in preview" :key="ch.id">
            <span :class="ch.on ? 'text-success' : 'text-lumia-dark/30'">{{ ch.on ? '✓' : '✗' }}</span>
            {{ ch.label }}
          </li>
        </ul>
      </div>

      <div class="pt-2 flex items-center gap-3">
        <button type="submit" class="btn btn-primary" :class="{ loading: saving }">ذخیره</button>
        <span v-if="saved" class="text-success text-sm">ذخیره شد</span>
      </div>
      <div v-if="error" class="alert alert-error text-sm">{{ error }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { StoreContact, StoreSettings } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

const form = ref<StoreContact>({
  contact_sms_phone: '',
  contact_telegram: '',
  contact_whatsapp: '',
  contact_bale: '',
})

const preview = computed(() => [
  { id: 'sms', label: 'پیامک (SMS)', on: !!form.value.contact_sms_phone.trim() },
  { id: 'telegram', label: 'تلگرام', on: !!form.value.contact_telegram.trim() },
  { id: 'whatsapp', label: 'واتس‌اپ', on: !!form.value.contact_whatsapp.trim() },
  { id: 'bale', label: 'بله', on: !!form.value.contact_bale.trim() },
])

async function load() {
  try {
    const data = await apiFetch<StoreSettings>('/admin/settings/')
    form.value = {
      contact_sms_phone: data.contact_sms_phone || '',
      contact_telegram: data.contact_telegram || '',
      contact_whatsapp: data.contact_whatsapp || '',
      contact_bale: data.contact_bale || '',
    }
  } catch {
    error.value = 'خطا در بارگذاری تنظیمات'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  saved.value = false
  error.value = ''
  try {
    await apiFetch('/admin/settings/', { method: 'PATCH', body: { ...form.value } })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ذخیره'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
