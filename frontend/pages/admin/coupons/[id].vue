<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <h2 class="font-bold text-lumia-dark">{{ isNew ? 'کد تخفیف جدید' : 'ویرایش کد تخفیف' }}</h2>
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-4">
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
            <div class="flex gap-3 pt-2">
              <button type="submit" class="btn btn-primary" :class="{ loading: saving }">ذخیره</button>
              <button v-if="!isNew" type="button" class="btn btn-error btn-outline" @click="deleteCoupon">حذف</button>
            </div>
            <div v-if="error" class="alert alert-error text-sm">{{ error }}</div>
          </form>
        </div>

        <!-- Usage history -->
        <div v-if="!isNew && coupon?.usage?.length" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">تاریخچه استفاده</h3>
          <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full text-sm">
            <thead>
              <tr class="text-lumia-dark/60 text-xs">
                <th class="text-right font-medium">کاربر</th>
                <th class="text-right font-medium">شماره سفارش</th>
                <th class="text-right font-medium">تاریخ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in coupon.usage" :key="u.id">
                <td>{{ u.user_phone }}</td>
                <td>{{ u.order_number || '—' }}</td>
                <td>{{ formatDate(u.used_at) }}</td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const route = useRoute()
const router = useRouter()
const { apiFetch, formatDate } = useApi()

const isNew = computed(() => route.params.id === 'new')
const coupon = ref<any>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = ref({
  code: '', coupon_type: 'percent', value: 0, min_order_amount: 0,
  max_uses: null as number | null, per_user_limit: 1,
  is_active: true, valid_from: '', valid_until: '',
})

async function load() {
  if (!isNew.value) {
    coupon.value = await apiFetch<any>(`/admin/coupons/${route.params.id}/`)
    const c = coupon.value
    form.value = {
      code: c.code, coupon_type: c.coupon_type, value: c.value,
      min_order_amount: c.min_order_amount, max_uses: c.max_uses,
      per_user_limit: c.per_user_limit, is_active: c.is_active,
      valid_from: c.valid_from?.slice(0, 16) ?? '',
      valid_until: c.valid_until?.slice(0, 16) ?? '',
    }
  }
  loading.value = false
}

async function save() {
  saving.value = true; error.value = ''
  try {
    const body = { ...form.value, valid_until: form.value.valid_until || null }
    if (isNew.value) {
      await apiFetch('/admin/coupons/', { method: 'POST', body })
      router.push('/admin/coupons')
    } else {
      await apiFetch(`/admin/coupons/${route.params.id}/`, { method: 'PATCH', body })
    }
  } catch (e: any) {
    error.value = JSON.stringify(e.data) ?? 'خطا'
  } finally { saving.value = false }
}

async function deleteCoupon() {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/coupons/${route.params.id}/`, { method: 'DELETE' })
  router.push('/admin/coupons')
}

onMounted(load)
</script>
