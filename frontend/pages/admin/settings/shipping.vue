<template>
  <div class="max-w-2xl">
    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-6" @submit.prevent="save">
      <div class="pb-4 border-b border-base-200">
        <h2 class="font-bold text-lumia-dark">هزینه ارسال</h2>
        <p class="text-xs text-lumia-dark/50 mt-1">
          این مبلغ به سفارش‌های جدید اضافه می‌شود. سفارش‌های ثبت‌شده تغییر نمی‌کنند.
        </p>
      </div>

      <div>
        <label for="shipping-cost" class="label-text text-xs block mb-1">هزینه ارسال هر بسته (تومان)</label>
        <input
          id="shipping-cost"
          v-model.number="form.shipping_cost"
          type="number"
          min="0"
          step="1000"
          class="input input-bordered w-full"
          :class="{ 'input-error': errors.shipping_cost }"
          dir="ltr"
          required
        />
        <p v-if="errors.shipping_cost" class="text-error text-xs mt-1.5">{{ errors.shipping_cost }}</p>
        <p v-else class="text-xs text-lumia-dark/40 mt-1">
          {{ form.shipping_cost > 0 ? toWords(form.shipping_cost) : 'ارسال برای همه سفارش‌ها رایگان می‌شود' }}
        </p>
      </div>

      <div>
        <label for="free-threshold" class="label-text text-xs block mb-1">
          خرید بیشتر از این مبلغ، ارسال رایگان (تومان)
        </label>
        <input
          id="free-threshold"
          v-model.number="form.free_shipping_threshold"
          type="number"
          min="0"
          step="1000"
          class="input input-bordered w-full"
          :class="{ 'input-error': errors.free_shipping_threshold }"
          dir="ltr"
        />
        <p v-if="errors.free_shipping_threshold" class="text-error text-xs mt-1.5">{{ errors.free_shipping_threshold }}</p>
        <p v-else class="text-xs text-lumia-dark/40 mt-1">
          {{ form.free_shipping_threshold > 0 ? toWords(form.free_shipping_threshold) : '۰ یعنی ارسال رایگان غیرفعال است و هزینه از همه سفارش‌ها گرفته می‌شود' }}
        </p>
      </div>

      <div class="rounded-xl bg-lumia-cream/30 border border-lumia-cream p-4 text-sm text-lumia-dark/70 space-y-1">
        <p class="font-bold text-lumia-dark">پیش‌نمایش برای مشتری:</p>
        <p v-for="row in preview" :key="row.label">{{ row.label }} ← {{ row.value }}</p>
        <p class="text-xs text-lumia-dark/40 pt-1">
          کد تخفیف از نوع «ارسال رایگان» همیشه هزینه ارسال را صفر می‌کند، حتی زیر این مبلغ.
        </p>
      </div>

      <div class="pt-2 flex items-center gap-3">
        <button type="submit" class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="loading loading-spinner loading-sm" />
          <span v-else>ذخیره</span>
        </button>
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
const errors = reactive({ shipping_cost: '', free_shipping_threshold: '' })

const form = ref<Pick<StoreSettings, 'shipping_cost' | 'free_shipping_threshold'>>({
  shipping_cost: 150000,
  free_shipping_threshold: 0,
})

/** Sample baskets either side of the threshold, so the effect is obvious. */
const preview = computed(() => {
  const threshold = form.value.free_shipping_threshold
  const cost = form.value.shipping_cost
  if (!threshold) {
    return [{ label: 'هر سفارش', value: cost ? `ارسال ${formatPrice(cost)}` : 'ارسال رایگان' }]
  }
  return [
    { label: `سبد کمتر از ${formatPrice(threshold)}`, value: cost ? `ارسال ${formatPrice(cost)}` : 'ارسال رایگان' },
    { label: `سبد ${formatPrice(threshold)} و بیشتر`, value: 'ارسال رایگان' },
  ]
})

function toWords(value: number) {
  const millions = value / 10_000_000
  if (millions >= 1) return `یعنی ${millions.toLocaleString('fa-IR')} میلیون تومان`
  return `یعنی ${(value / 1000).toLocaleString('fa-IR')} هزار تومان`
}

function validate() {
  errors.shipping_cost = ''
  errors.free_shipping_threshold = ''
  if (!Number.isFinite(form.value.shipping_cost) || form.value.shipping_cost < 0) {
    errors.shipping_cost = 'هزینه ارسال نمی‌تواند منفی یا خالی باشد'
  }
  if (!Number.isFinite(form.value.free_shipping_threshold) || form.value.free_shipping_threshold < 0) {
    errors.free_shipping_threshold = 'این مبلغ نمی‌تواند منفی یا خالی باشد'
  }
  return !errors.shipping_cost && !errors.free_shipping_threshold
}

async function load() {
  try {
    const data = await apiFetch<StoreSettings>('/admin/settings/')
    form.value.shipping_cost = data.shipping_cost ?? 150000
    form.value.free_shipping_threshold = data.free_shipping_threshold ?? 0
  } catch {
    error.value = 'خطا در بارگذاری تنظیمات'
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!validate()) return
  saving.value = true
  saved.value = false
  error.value = ''
  try {
    await apiFetch('/admin/settings/', {
      method: 'PATCH',
      body: {
        shipping_cost: form.value.shipping_cost,
        free_shipping_threshold: form.value.free_shipping_threshold,
      },
    })
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string; shipping_cost?: string[]; free_shipping_threshold?: string[] } }
    errors.shipping_cost = err.data?.shipping_cost?.[0] || ''
    errors.free_shipping_threshold = err.data?.free_shipping_threshold?.[0] || ''
    error.value = err.data?.detail
      || (errors.shipping_cost || errors.free_shipping_threshold ? '' : 'خطا در ذخیره')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
