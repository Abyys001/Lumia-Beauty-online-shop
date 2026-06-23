<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/admin/orders" class="btn btn-ghost btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        بازگشت
      </NuxtLink>
      <h2 class="font-bold text-lumia-dark">سفارش {{ order?.order_number }}</h2>
      <AdminBadge v-if="order" :status="order.status" />
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Order items -->
      <div class="lg:col-span-2 space-y-4">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">اقلام سفارش</h3>
          <table class="table w-full">
            <thead>
              <tr class="text-lumia-dark/60 text-xs">
                <th class="text-right font-medium">محصول</th>
                <th class="text-right font-medium">قیمت</th>
                <th class="text-right font-medium">تعداد</th>
                <th class="text-right font-medium">جمع</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in order.items" :key="item.id">
                <td class="text-sm">{{ item.product_name }}</td>
                <td class="text-sm">{{ formatPrice(item.product_price) }}</td>
                <td class="text-sm">{{ item.quantity }}</td>
                <td class="text-sm font-bold">{{ formatPrice(item.subtotal) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="mt-4 space-y-1 text-sm pt-3 border-t border-base-200">
            <div class="flex justify-between"><span class="text-lumia-dark/60">جمع کل:</span><span>{{ formatPrice(order.subtotal) }}</span></div>
            <div v-if="order.discount_amount" class="flex justify-between text-success"><span>تخفیف:</span><span>- {{ formatPrice(order.discount_amount) }}</span></div>
            <div class="flex justify-between"><span class="text-lumia-dark/60">هزینه ارسال:</span><span>{{ order.free_shipping ? 'رایگان' : formatPrice(order.shipping_cost) }}</span></div>
            <div class="flex justify-between font-bold text-base border-t pt-2 mt-2">
              <span>مبلغ نهایی:</span><span class="text-lumia-gold">{{ formatPrice(order.total) }}</span>
            </div>
          </div>
        </div>

        <!-- Shipping info -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">اطلاعات ارسال</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-lumia-dark/50">گیرنده:</span> {{ order.shipping_name }}</div>
            <div><span class="text-lumia-dark/50">تلفن:</span> {{ order.shipping_phone }}</div>
            <div><span class="text-lumia-dark/50">استان:</span> {{ order.shipping_province }}</div>
            <div><span class="text-lumia-dark/50">شهر:</span> {{ order.shipping_city }}</div>
            <div class="col-span-2"><span class="text-lumia-dark/50">آدرس:</span> {{ order.shipping_address }}</div>
            <div><span class="text-lumia-dark/50">کد پستی:</span> {{ order.shipping_postal_code }}</div>
            <div v-if="order.tracking_number"><span class="text-lumia-dark/50">کد رهگیری:</span> {{ order.tracking_number }}</div>
          </div>
        </div>
      </div>

      <!-- Side -->
      <div class="space-y-4">
        <!-- Customer -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-3">خریدار</h3>
          <div class="text-sm space-y-1">
            <div class="font-medium">{{ order.user_phone }}</div>
            <div class="text-lumia-dark/50">تاریخ: {{ formatDate(order.created_at) }}</div>
            <div v-if="order.coupon_code" class="text-lumia-dark/50">کوپن: {{ order.coupon_code }}</div>
          </div>
          <div class="mt-3">
            <div class="text-xs text-lumia-dark/50 mb-1">وضعیت پرداخت</div>
            <AdminBadge v-if="order.payment_status" :status="order.payment_status" />
            <span v-else class="text-xs text-lumia-dark/30">ندارد</span>
          </div>
        </div>

        <!-- Status update -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-3">تغییر وضعیت</h3>
          <select v-model="newStatus" class="select select-bordered w-full select-sm mb-3">
            <option value="pending">در انتظار پرداخت</option>
            <option value="paid">پرداخت شده</option>
            <option value="processing">در حال پردازش</option>
            <option value="shipped">ارسال شده</option>
            <option value="delivered">تحویل داده شده</option>
            <option value="cancelled">لغو شده</option>
            <option value="refunded">مرجوع شده</option>
          </select>
          <div v-if="newStatus === 'shipped'" class="mb-3">
            <label class="label-text text-xs block mb-1">کد رهگیری (۲۴ رقم)</label>
            <input v-model="trackingNumber" type="text" class="input input-bordered w-full input-sm" dir="ltr" maxlength="24" />
          </div>
          <button class="btn btn-primary w-full btn-sm" :class="{ loading: updating }" @click="updateStatus">اعمال تغییر</button>
          <div v-if="statusError" class="text-error text-xs mt-2">{{ statusError }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const route = useRoute()
const { apiFetch, formatPrice, formatDate } = useApi()

const order = ref<any>(null)
const loading = ref(true)
const newStatus = ref('')
const trackingNumber = ref('')
const updating = ref(false)
const statusError = ref('')

async function load() {
  loading.value = true
  order.value = await apiFetch<any>(`/admin/orders/${route.params.id}/`)
  newStatus.value = order.value.status
  trackingNumber.value = order.value.tracking_number ?? ''
  loading.value = false
}

async function updateStatus() {
  updating.value = true
  statusError.value = ''
  try {
    const body: Record<string, string> = { status: newStatus.value }
    if (newStatus.value === 'shipped') body.tracking_number = trackingNumber.value
    const updated = await apiFetch<any>(`/admin/orders/${route.params.id}/`, { method: 'PATCH', body })
    order.value = updated
  } catch (e: any) {
    statusError.value = e.data?.tracking_number ?? e.data?.detail ?? 'خطا در ذخیره'
  } finally {
    updating.value = false
  }
}

onMounted(load)
</script>
