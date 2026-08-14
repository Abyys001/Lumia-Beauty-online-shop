<template>
  <div>
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <h2 class="font-bold text-lumia-dark">سفارش {{ order?.order_number }}</h2>
      <AdminBadge v-if="order" :status="order.status" />
      <span v-if="order?.purchase_code" class="font-mono text-sm text-lumia-gold bg-lumia-gold/10 rounded-lg px-3 py-1.5" dir="ltr">کد خرید: {{ order.purchase_code }}</span>
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else-if="order" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Order items -->
      <div class="lg:col-span-2 space-y-4">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">اقلام سفارش</h3>
          <div class="overflow-x-auto w-full min-w-0">
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
          </div>
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
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div><span class="text-lumia-dark/50">گیرنده:</span> {{ order.shipping_name }}</div>
            <div><span class="text-lumia-dark/50">تلفن:</span> {{ order.shipping_phone }}</div>
            <div><span class="text-lumia-dark/50">استان:</span> {{ order.shipping_province }}</div>
            <div><span class="text-lumia-dark/50">شهر:</span> {{ order.shipping_city }}</div>
            <div class="col-span-2"><span class="text-lumia-dark/50">آدرس:</span> {{ order.shipping_address }}</div>
            <div><span class="text-lumia-dark/50">کد پستی:</span> {{ order.shipping_postal_code }}</div>
            <div v-if="order.shipping_plate_number"><span class="text-lumia-dark/50">پلاک خودرو:</span> {{ order.shipping_plate_number }}</div>
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
            <div class="font-medium">{{ order.user_full_name || order.user_phone }}</div>
            <div v-if="order.user_full_name" class="text-lumia-dark/50">{{ order.user_phone }}</div>
            <div class="text-lumia-dark/50">تاریخ: {{ formatDate(order.created_at) }}</div>
            <div v-if="order.coupon_code" class="text-lumia-dark/50">کوپن: {{ order.coupon_code }}</div>
          </div>
          <div class="mt-3">
            <div class="text-xs text-lumia-dark/50 mb-1">وضعیت پرداخت</div>
            <AdminBadge v-if="order.payment_status" :status="order.payment_status" />
            <span v-else class="text-xs text-lumia-dark/30">ندارد</span>
          </div>
          <button
            v-if="order.payment_status !== 'success'"
            class="btn btn-primary w-full btn-sm mt-4"
            :class="{ loading: markingPaid }"
            @click="markPaid"
          >
            ثبت پرداخت کارت‌به‌کارت
          </button>
          <div v-if="markPaidMsg" class="text-xs mt-2" :class="markPaidOk ? 'text-success' : 'text-error'">{{ markPaidMsg }}</div>
        </div>

        <!-- Payment details -->
        <div v-if="order.payment_detail" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-3">جزئیات پرداخت</h3>
          <div class="text-xs space-y-1.5 font-mono break-all" dir="ltr">
            <div v-if="order.payment_detail.authority"><span class="text-lumia-dark/50">Authority:</span> {{ order.payment_detail.authority }}</div>
            <div v-if="order.payment_detail.ref_id"><span class="text-lumia-dark/50">Ref ID:</span> {{ order.payment_detail.ref_id }}</div>
            <div v-if="order.payment_detail.card_pan"><span class="text-lumia-dark/50">Card:</span> {{ order.payment_detail.card_pan }}</div>
            <div v-if="order.payment_detail.fee"><span class="text-lumia-dark/50">Fee:</span> {{ order.payment_detail.fee }}</div>
            <div v-if="order.payment_detail.paid_at"><span class="text-lumia-dark/50">Paid:</span> {{ formatDate(order.payment_detail.paid_at) }}</div>
          </div>
          <div v-if="order.payment_id && order.payment_status === 'success'" class="flex flex-wrap gap-2 mt-4">
            <button class="btn btn-outline btn-xs" :class="{ loading: inquiring }" @click="runInquiry">استعلام</button>
            <button
              v-if="order.payment_detail.is_recent"
              class="btn btn-warning btn-xs"
              :class="{ loading: reversing }"
              @click="runReverse"
            >
              برگشت فوری
            </button>
            <button class="btn btn-error btn-xs" :class="{ loading: refunding }" @click="runRefund">مرجوعی</button>
          </div>
          <div v-if="paymentActionMsg" class="text-xs mt-2" :class="paymentActionOk ? 'text-success' : 'text-error'">{{ paymentActionMsg }}</div>
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
const inquiring = ref(false)
const reversing = ref(false)
const refunding = ref(false)
const paymentActionMsg = ref('')
const paymentActionOk = ref(false)
const markingPaid = ref(false)
const markPaidMsg = ref('')
const markPaidOk = ref(false)

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

async function markPaid() {
  if (!order.value || !confirm('پرداخت کارت‌به‌کارت برای این سفارش تأیید شود؟')) return
  markingPaid.value = true
  markPaidMsg.value = ''
  statusError.value = ''
  try {
    const updated = await apiFetch<any>(`/admin/orders/${route.params.id}/mark-paid/`, { method: 'POST' })
    order.value = updated
    newStatus.value = updated.status
    markPaidOk.value = true
    markPaidMsg.value = 'پرداخت با موفقیت ثبت شد'
  } catch (e: any) {
    markPaidOk.value = false
    markPaidMsg.value = e.data?.detail || 'ثبت پرداخت ناموفق'
  } finally {
    markingPaid.value = false
  }
}

async function runInquiry() {
  if (!order.value?.payment_id) return
  inquiring.value = true
  paymentActionMsg.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string; data: Record<string, unknown> }>(
      `/admin/payments/${order.value.payment_id}/inquiry/`,
      { method: 'POST' },
    )
    paymentActionOk.value = res.success
    paymentActionMsg.value = res.message || JSON.stringify(res.data?.status ?? res.data)
  } catch (e: any) {
    paymentActionOk.value = false
    paymentActionMsg.value = e.data?.detail || 'استعلام ناموفق'
  } finally { inquiring.value = false }
}

async function runReverse() {
  if (!order.value?.payment_id || !confirm('برگشت فوری تراکنش انجام شود؟')) return
  reversing.value = true
  paymentActionMsg.value = ''
  try {
    await apiFetch(`/admin/payments/${order.value.payment_id}/reverse/`, { method: 'POST' })
    paymentActionOk.value = true
    paymentActionMsg.value = 'برگشت فوری با موفقیت انجام شد'
    await load()
  } catch (e: any) {
    paymentActionOk.value = false
    paymentActionMsg.value = e.data?.detail || 'برگشت ناموفق'
  } finally { reversing.value = false }
}

async function runRefund() {
  if (!order.value?.payment_id || !confirm('مرجوعی کامل سفارش انجام شود؟')) return
  refunding.value = true
  paymentActionMsg.value = ''
  try {
    await apiFetch(`/admin/payments/${order.value.payment_id}/refund/`, {
      method: 'POST',
      body: { method: 'instant' },
    })
    paymentActionOk.value = true
    paymentActionMsg.value = 'درخواست مرجوعی ثبت شد'
    await load()
  } catch (e: any) {
    paymentActionOk.value = false
    paymentActionMsg.value = e.data?.detail || 'مرجوعی ناموفق'
  } finally { refunding.value = false }
}

onMounted(load)
</script>
