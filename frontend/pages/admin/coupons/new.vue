<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <h2 class="font-bold text-lumia-dark">کد تخفیف جدید</h2>
    </div>

    <div class="max-w-2xl">
      <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
        <form @submit.prevent="save" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="label-text text-xs block mb-1">کد تخفیف *</label>
              <input v-model="form.code" type="text" class="input input-bordered w-full" dir="ltr" required />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">نوع *</label>
              <select v-model="form.coupon_type" class="select select-bordered w-full">
                <option value="percent">درصدی</option>
                <option value="fixed">مبلغ ثابت</option>
                <option value="free_shipping">ارسال رایگان</option>
              </select>
            </div>
            <div>
              <label class="label-text text-xs block mb-1">مقدار</label>
              <input v-model.number="form.value" type="number" min="0" class="input input-bordered w-full" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">حداقل مبلغ سفارش</label>
              <input v-model.number="form.min_order_amount" type="number" min="0" class="input input-bordered w-full" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">حداکثر استفاده (خالی = نامحدود)</label>
              <input v-model.number="form.max_uses" type="number" min="0" class="input input-bordered w-full" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">محدودیت هر کاربر</label>
              <input v-model.number="form.per_user_limit" type="number" min="1" class="input input-bordered w-full" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">تاریخ شروع</label>
              <input v-model="form.valid_from" type="datetime-local" class="input input-bordered w-full input-sm" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs block mb-1">تاریخ انقضا (اختیاری)</label>
              <input v-model="form.valid_until" type="datetime-local" class="input input-bordered w-full input-sm" dir="ltr" />
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">فعال</span>
          </label>
          <div class="pt-2">
            <button type="submit" class="btn btn-primary" :class="{ loading: saving }">ایجاد کد تخفیف</button>
          </div>
          <div v-if="error" class="alert alert-error text-sm">{{ error }}</div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const router = useRouter()
const { apiFetch } = useApi()
const saving = ref(false)
const error = ref('')

const form = ref({
  code: '', coupon_type: 'percent', value: 0, min_order_amount: 0,
  max_uses: null as number | null, per_user_limit: 1,
  is_active: true, valid_from: '', valid_until: '',
})

async function save() {
  saving.value = true; error.value = ''
  try {
    const body = { ...form.value, valid_until: form.value.valid_until || null }
    const created = await apiFetch<any>('/admin/coupons/', { method: 'POST', body })
    router.push(`/admin/coupons/${created.id}`)
  } catch (e: any) {
    error.value = JSON.stringify(e.data) ?? 'خطا'
  } finally { saving.value = false }
}
</script>
