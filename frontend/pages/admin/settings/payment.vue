<template>
  <div class="max-w-2xl">
    <NuxtLink to="/admin/settings" class="text-sm text-lumia-gold hover:underline mb-4 inline-block">
      ← بازگشت به تنظیمات
    </NuxtLink>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else @submit.prevent="save" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-5">
      <h2 class="font-bold text-lumia-dark pb-4 border-b border-base-200">درگاه پرداخت (Zarinpal)</h2>

      <div>
        <label class="label-text text-xs block mb-1">Merchant ID</label>
        <input v-model="form.zarinpal_merchant_id" type="text" class="input input-bordered w-full" dir="ltr" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
        <p class="text-xs text-lumia-dark/40 mt-1">شناسه درگاه زرین‌پال برای دریافت پرداخت واقعی</p>
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
import type { StoreSettings } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

const form = ref<StoreSettings>({ zarinpal_merchant_id: '' })

async function load() {
  try {
    form.value = await apiFetch<StoreSettings>('/admin/settings/')
  } catch {
    error.value = 'خطا در بارگذاری تنظیمات'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true; saved.value = false; error.value = ''
  try {
    await apiFetch('/admin/settings/', { method: 'PATCH', body: form.value })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ذخیره'
  } finally { saving.value = false }
}

onMounted(load)
</script>
