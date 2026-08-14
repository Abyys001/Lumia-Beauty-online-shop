<template>
  <div class="max-w-2xl">
    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else @submit.prevent="save" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-5">
      <h2 class="font-bold text-lumia-dark pb-4 border-b border-base-200">هزینه ارسال بسته</h2>

      <div>
        <label class="label-text text-xs block mb-1">هزینه ارسال هر بسته (تومان)</label>
        <input
          v-model.number="form.shipping_cost"
          type="number"
          min="0"
          step="1000"
          class="input input-bordered w-full"
          dir="ltr"
          required
        />
        <p class="text-xs text-lumia-dark/40 mt-1">هزینه ثابت ارسال که برای هر سفارش از مشتری دریافت می‌شود</p>
      </div>

      <div class="rounded-xl bg-lumia-cream/30 border border-lumia-cream p-4 text-sm text-lumia-dark/70 space-y-1">
        <p><strong>پیش‌نمایش:</strong></p>
        <p>هر سفارش → ارسال {{ formatPrice(form.shipping_cost) }}</p>
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

const { apiFetch, formatPrice } = useApi()
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')

const form = ref<Pick<StoreSettings, 'shipping_cost'>>({
  shipping_cost: 150000,
})

async function load() {
  try {
    const data = await apiFetch<StoreSettings>('/admin/settings/')
    form.value.shipping_cost = data.shipping_cost ?? 150000
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
    await apiFetch('/admin/settings/', {
      method: 'PATCH',
      body: {
        shipping_cost: form.value.shipping_cost,
      },
    })
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
