<template>
  <div class="admin-page max-w-5xl space-y-6">
    <!-- Search hero -->
    <div class="rounded-3xl border-2 border-lumia-gold/40 bg-gradient-to-bl from-lumia-gold/15 to-white p-5 sm:p-8 shadow-sm">
      <h1 class="text-xl sm:text-2xl font-black text-lumia-dark">پیگیری کد خرید مشتری</h1>
      <p class="mt-1 text-sm text-lumia-dark/60">
        کد خرید ۶ رقمی (یا شماره سفارش LB…) را وارد کنید تا تمام اطلاعات مشتری نمایش داده شود.
      </p>

      <form class="mt-5 flex flex-col sm:flex-row gap-3" @submit.prevent="lookup">
        <input
          ref="codeInput"
          v-model="code"
          class="input input-bordered input-lg flex-1 rounded-2xl text-center font-mono text-2xl sm:text-3xl font-black tracking-[0.3em]"
          dir="ltr"
          placeholder="------"
          inputmode="numeric"
          autocomplete="off"
          @input="onInput"
        />
        <button
          type="submit"
          class="btn btn-primary btn-lg rounded-2xl px-8 font-bold"
          :disabled="loading || !code"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm" />
          <span v-else>جستجو</span>
        </button>
      </form>

      <p v-if="error" class="mt-3 rounded-xl bg-error/10 px-4 py-3 text-sm font-bold text-error">{{ error }}</p>

      <div v-if="recent.length" class="mt-4 flex flex-wrap items-center gap-2">
        <span class="text-xs text-lumia-dark/40">جستجوهای اخیر:</span>
        <button
          v-for="c in recent"
          :key="c"
          type="button"
          class="btn btn-xs rounded-full font-mono"
          dir="ltr"
          @click="code = c; lookup()"
        >
          {{ c }}
        </button>
      </div>
    </div>

    <!-- Result -->
    <div v-if="order" class="space-y-4">
      <!-- Summary strip -->
      <div class="rounded-3xl border-2 border-base-200 bg-white p-5 shadow-sm">
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p class="font-mono text-3xl font-black text-lumia-gold" dir="ltr">{{ order.purchase_code }}</p>
            <p class="mt-1 text-sm text-lumia-dark/50">
              سفارش <span class="font-mono" dir="ltr">{{ order.order_number }}</span> — {{ formatDate(order.created_at) }}
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <AdminBadge :status="order.status" />
            <span
              v-if="!isCancelled"
              class="rounded-full px-3 py-1 text-xs font-bold"
              :class="isPaid ? 'bg-success/15 text-success' : 'bg-warning/15 text-warning'"
            >
              {{ isPaid ? 'پرداخت تأیید شده' : 'در انتظار تأیید پرداخت' }}
            </span>
          </div>
        </div>

        <div class="mt-5 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl bg-lumia-cream/50 p-4 text-center">
            <p class="text-xs text-lumia-dark/50">مبلغ قابل دریافت</p>
            <p class="mt-1 text-2xl font-black text-lumia-dark">{{ formatPrice(order.total) }}</p>
            <p class="text-xs text-lumia-dark/40">تومان</p>
          </div>
          <div class="rounded-2xl bg-lumia-cream/50 p-4 text-center">
            <p class="text-xs text-lumia-dark/50">تعداد اقلام</p>
            <p class="mt-1 text-2xl font-black text-lumia-dark">{{ itemCount }}</p>
            <p class="text-xs text-lumia-dark/40">عدد</p>
          </div>
          <div class="rounded-2xl bg-lumia-cream/50 p-4 text-center">
            <p class="text-xs text-lumia-dark/50">هزینه ارسال</p>
            <p class="mt-1 text-2xl font-black text-lumia-dark">{{ formatPrice(order.shipping_cost) }}</p>
            <p class="text-xs text-lumia-dark/40">تومان</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="mt-5 flex flex-wrap gap-2">
          <button
            v-if="!isPaid && !isCancelled"
            class="btn btn-success rounded-full font-bold text-white"
            :disabled="marking"
            @click="markPaid"
          >
            <span v-if="marking" class="loading loading-spinner loading-sm" />
            <span v-else>✓ پرداخت را دریافت کردم — تأیید نهایی</span>
          </button>
          <button class="btn btn-outline rounded-full" @click="copyAll">
            {{ copied ? 'کپی شد ✓' : 'کپی اطلاعات ارسال' }}
          </button>
          <a
            v-if="waLink"
            :href="waLink"
            target="_blank"
            rel="noopener"
            class="btn btn-outline rounded-full"
          >
            واتس‌اپ مشتری
          </a>
          <a :href="`tel:${order.shipping_phone}`" class="btn btn-outline rounded-full">تماس با مشتری</a>
          <NuxtLink :to="`/admin/orders/${order.id}`" class="btn btn-ghost rounded-full">
            صفحه کامل سفارش
          </NuxtLink>
        </div>
        <p v-if="actionMsg" class="mt-3 text-sm font-bold" :class="actionOk ? 'text-success' : 'text-error'">
          {{ actionMsg }}
        </p>
      </div>

      <!-- Postal tracking -->
      <div v-if="isPaid && !isCancelled" class="rounded-3xl border-2 border-info/30 bg-info/5 p-5 shadow-sm">
        <h2 class="font-black text-lumia-dark">کد رهگیری مرسوله پستی</h2>
        <p class="mt-1 text-sm text-lumia-dark/60">
          بعد از پست کردن بسته، کد رهگیری ۲۴ رقمی روی رسید پست را اینجا وارد کنید. سفارش «ارسال شده» می‌شود و مشتری کد را در صفحه سفارش خود می‌بیند.
        </p>
        <div class="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            v-model="tracking"
            class="input input-bordered flex-1 rounded-2xl text-center font-mono tracking-widest"
            dir="ltr"
            inputmode="numeric"
            maxlength="24"
            placeholder="کد ۲۴ رقمی"
            @input="onTrackingInput"
          />
          <button
            class="btn btn-primary rounded-2xl px-8 font-bold"
            :disabled="saving || tracking.length !== 24"
            @click="saveTracking"
          >
            <span v-if="saving" class="loading loading-spinner loading-sm" />
            <span v-else>{{ isShipped ? 'به‌روزرسانی کد رهگیری' : 'ثبت کد و ارسال شد' }}</span>
          </button>
        </div>
        <p class="mt-2 text-xs text-lumia-dark/40" dir="ltr">{{ tracking.length }} / 24</p>
        <p v-if="shipMsg" class="mt-3 text-sm font-bold" :class="shipOk ? 'text-success' : 'text-error'">{{ shipMsg }}</p>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <!-- Customer + shipping -->
        <div class="rounded-3xl border-2 border-base-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 font-black text-lumia-dark">اطلاعات مشتری و ارسال</h2>
          <dl class="space-y-3 text-sm">
            <div v-for="row in customerRows" :key="row.label" class="flex items-start justify-between gap-3 border-b border-base-200 pb-2 last:border-0">
              <dt class="shrink-0 text-lumia-dark/50">{{ row.label }}</dt>
              <dd class="flex-1 text-left font-bold text-lumia-dark" :dir="row.ltr ? 'ltr' : 'rtl'">
                {{ row.value || '—' }}
              </dd>
            </div>
          </dl>
        </div>

        <!-- Items + invoice -->
        <div class="rounded-3xl border-2 border-base-200 bg-white p-5 shadow-sm">
          <h2 class="mb-4 font-black text-lumia-dark">اقلام سفارش</h2>
          <div class="space-y-2">
            <div
              v-for="item in order.items"
              :key="item.id"
              class="flex items-start justify-between gap-2 border-b border-base-200 pb-2 text-sm"
            >
              <span class="flex-1 leading-6">{{ item.product_name }}</span>
              <span class="shrink-0 text-lumia-dark/50">× {{ item.quantity }}</span>
              <span class="shrink-0 font-bold">{{ formatPrice(item.subtotal) }}</span>
            </div>
          </div>
          <div class="mt-4 space-y-2 text-sm">
            <div class="flex justify-between"><span class="text-lumia-dark/50">جمع اقلام</span><span>{{ formatPrice(order.subtotal) }}</span></div>
            <div v-if="order.discount_amount" class="flex justify-between text-success"><span>تخفیف {{ order.coupon_code }}</span><span>− {{ formatPrice(order.discount_amount) }}</span></div>
            <div class="flex justify-between"><span class="text-lumia-dark/50">ارسال</span><span>{{ formatPrice(order.shipping_cost) }}</span></div>
            <div class="flex justify-between border-t-2 border-lumia-gold/30 pt-3 text-lg font-black">
              <span>مبلغ نهایی</span><span class="text-lumia-gold">{{ formatPrice(order.total) }}</span>
            </div>
          </div>
          <p v-if="order.note" class="mt-4 rounded-xl bg-lumia-cream/50 p-3 text-sm leading-6">
            <span class="font-bold">یادداشت مشتری:</span> {{ order.note }}
          </p>
        </div>
      </div>
    </div>

    <!-- Latest purchases -->
    <div class="rounded-3xl border-2 border-base-200 bg-white shadow-sm">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-base-200 p-5">
        <div>
          <h2 class="font-black text-lumia-dark">آخرین خریدها</h2>
          <p class="mt-0.5 text-xs text-lumia-dark/50">روی هر ردیف بزنید تا اطلاعات کامل آن سفارش باز شود.</p>
        </div>
        <button class="btn btn-ghost btn-sm rounded-full" :disabled="recentPending" @click="refreshRecent()">
          <span v-if="recentPending" class="loading loading-spinner loading-xs" />
          <span v-else>به‌روزرسانی</span>
        </button>
      </div>

      <div class="flex flex-wrap gap-2 px-5 pt-4">
        <button
          v-for="f in statusFilters"
          :key="f.value"
          type="button"
          class="btn btn-xs rounded-full font-bold"
          :class="statusFilter === f.value ? 'btn-primary' : 'btn-ghost border border-base-200'"
          @click="statusFilter = f.value"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="recentPending && !recentOrders.length" class="p-5 space-y-2">
        <div v-for="n in 4" :key="n" class="h-16 rounded-2xl bg-base-200/60 animate-pulse" />
      </div>

      <ul v-else-if="recentOrders.length" class="divide-y divide-base-200">
        <li v-for="row in recentOrders" :key="row.id">
          <button
            type="button"
            class="flex w-full flex-wrap items-center gap-3 p-4 text-right transition-colors hover:bg-lumia-cream/40"
            :class="{ 'bg-lumia-gold/10': order?.id === row.id }"
            @click="openOrder(row)"
          >
            <span class="font-mono text-xl font-black text-lumia-gold" dir="ltr">{{ row.purchase_code }}</span>
            <span class="min-w-0 flex-1">
              <span class="block truncate font-bold text-lumia-dark">{{ row.shipping_name || row.user_phone || '—' }}</span>
              <span class="block text-xs text-lumia-dark/50">
                {{ timeAgo(row.created_at) }} — {{ row.item_count }} قلم
              </span>
            </span>
            <span class="shrink-0 font-bold text-lumia-dark">{{ formatPrice(row.total) }}</span>
            <AdminBadge :status="row.status" />
          </button>
        </li>
      </ul>

      <p v-else class="p-10 text-center text-sm text-lumia-dark/50">
        خریدی با این وضعیت ثبت نشده است.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Order, PaginatedResponse } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

interface AdminOrder extends Order {
  user_phone?: string
  user_full_name?: string
  payment_status?: string | null
}

interface AdminOrderRow {
  id: string
  order_number: string
  purchase_code: string
  user_phone?: string
  shipping_name?: string
  status: string
  status_display: string
  item_count: number
  total: number
  created_at: string
}

const { apiFetch, formatPrice, formatDate } = useApi()

const code = ref('')
const codeInput = ref<HTMLInputElement | null>(null)
const order = ref<AdminOrder | null>(null)
const loading = ref(false)
const error = ref('')
const marking = ref(false)
const actionMsg = ref('')
const actionOk = ref(false)
const copied = ref(false)
const recent = ref<string[]>([])
const tracking = ref('')
const saving = ref(false)
const shipMsg = ref('')
const shipOk = ref(false)

const RECENT_KEY = 'lumia_recent_lookups'

const statusFilters = [
  { value: '', label: 'همه' },
  { value: 'pending', label: 'در انتظار پرداخت' },
  { value: 'paid', label: 'پرداخت شده' },
  { value: 'shipped', label: 'ارسال شده' },
] as const

const statusFilter = ref<string>('')

const { data: recentPage, pending: recentPending, refresh: refreshRecent } = await useAsyncData(
  'admin-lookup-recent',
  () => apiFetch<PaginatedResponse<AdminOrderRow>>('/admin/orders/', {
    query: { page_size: 8, ...(statusFilter.value ? { status: statusFilter.value } : {}) },
  }),
  { server: false, watch: [statusFilter] },
)

const recentOrders = computed(() => recentPage.value?.results ?? [])

const PAID_STATUSES = ['paid', 'processing', 'shipped', 'delivered']
const isPaid = computed(() =>
  order.value?.payment_status === 'success' || PAID_STATUSES.includes(order.value?.status ?? ''),
)
const isCancelled = computed(() => ['cancelled', 'refunded'].includes(order.value?.status ?? ''))
const isShipped = computed(() => ['shipped', 'delivered'].includes(order.value?.status ?? ''))
const itemCount = computed(() => order.value?.items?.reduce((n, i) => n + i.quantity, 0) ?? 0)

const waLink = computed(() => {
  const phone = order.value?.shipping_phone?.replace(/\D/g, '')
  if (!phone) return ''
  const intl = phone.startsWith('0') ? `98${phone.slice(1)}` : phone
  return `https://wa.me/${intl}`
})

const customerRows = computed(() => {
  const o = order.value
  if (!o) return []
  return [
    { label: 'نام گیرنده', value: o.shipping_name, ltr: false },
    { label: 'موبایل گیرنده', value: o.shipping_phone, ltr: true },
    { label: 'موبایل حساب کاربری', value: o.user_phone, ltr: true },
    { label: 'استان / شهر', value: [o.shipping_province, o.shipping_city].filter(Boolean).join(' — '), ltr: false },
    { label: 'آدرس', value: o.shipping_address, ltr: false },
    { label: 'پلاک و واحد', value: o.shipping_plate_number, ltr: true },
    { label: 'کد پستی', value: o.shipping_postal_code, ltr: true },
  ]
})

function toAsciiDigits(value: string) {
  return value
    .replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)))
}

function onInput() {
  // Accept Persian/Arabic digits and strip anything that is not a code character.
  code.value = toAsciiDigits(code.value)
    .replace(/[^0-9a-zA-Z]/g, '')
    .toUpperCase()
    .slice(0, 20)
}

function onTrackingInput() {
  tracking.value = toAsciiDigits(tracking.value).replace(/\D/g, '').slice(0, 24)
}

function pushRecent(value: string) {
  recent.value = [value, ...recent.value.filter((c) => c !== value)].slice(0, 6)
  if (import.meta.client) localStorage.setItem(RECENT_KEY, JSON.stringify(recent.value))
}

function openOrder(row: AdminOrderRow) {
  code.value = row.purchase_code || row.order_number
  lookup()
}

function timeAgo(iso: string) {
  const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return 'همین حالا'
  if (seconds < 3600) return `${Math.floor(seconds / 60)} دقیقه پیش`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} ساعت پیش`
  const days = Math.floor(seconds / 86400)
  return days < 30 ? `${days} روز پیش` : formatDate(iso)
}

async function lookup() {
  if (!code.value) return
  loading.value = true
  error.value = ''
  actionMsg.value = ''
  order.value = null
  try {
    order.value = await apiFetch<AdminOrder>(`/admin/orders/lookup/?code=${encodeURIComponent(code.value)}`)
    tracking.value = order.value.tracking_number ?? ''
    shipMsg.value = ''
    pushRecent(code.value)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'سفارشی با این کد پیدا نشد'
  } finally {
    loading.value = false
  }
}

async function markPaid() {
  if (!order.value) return
  marking.value = true
  actionMsg.value = ''
  try {
    order.value = await apiFetch<AdminOrder>(`/admin/orders/${order.value.id}/mark-paid/`, { method: 'POST' })
    actionOk.value = true
    actionMsg.value = 'پرداخت ثبت شد — موجودی کسر و سفارش به وضعیت «پرداخت شده» رفت.'
    refreshRecent()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    actionOk.value = false
    actionMsg.value = err.data?.detail || 'ثبت پرداخت ناموفق بود'
  } finally {
    marking.value = false
  }
}

async function saveTracking() {
  if (!order.value || tracking.value.length !== 24) return
  saving.value = true
  shipMsg.value = ''
  try {
    order.value = await apiFetch<AdminOrder>(`/admin/orders/${order.value.id}/`, {
      method: 'PATCH',
      body: { status: 'shipped', tracking_number: tracking.value },
    })
    shipOk.value = true
    shipMsg.value = 'کد رهگیری ثبت شد — سفارش «ارسال شده» است و مشتری کد را می‌بیند.'
    refreshRecent()
  } catch (e: unknown) {
    const err = e as { data?: { tracking_number?: string; detail?: string } }
    shipOk.value = false
    shipMsg.value = err.data?.tracking_number || err.data?.detail || 'ثبت کد رهگیری ناموفق بود'
  } finally {
    saving.value = false
  }
}

async function copyAll() {
  const o = order.value
  if (!o || !import.meta.client) return
  const text = [
    `کد خرید: ${o.purchase_code}`,
    `سفارش: ${o.order_number}`,
    `گیرنده: ${o.shipping_name} — ${o.shipping_phone}`,
    `آدرس: ${o.shipping_province}، ${o.shipping_city}، ${o.shipping_address}`,
    o.shipping_plate_number ? `پلاک و واحد: ${o.shipping_plate_number}` : '',
    o.shipping_postal_code ? `کد پستی: ${o.shipping_postal_code}` : '',
    `مبلغ: ${o.total.toLocaleString('fa-IR')} تومان`,
  ].filter(Boolean).join('\n')
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

const route = useRoute()

onMounted(() => {
  try {
    recent.value = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
  } catch {
    recent.value = []
  }
  const preset = (route.query.code as string) || ''
  if (preset) {
    code.value = preset
    onInput()
    lookup()
  } else {
    codeInput.value?.focus()
  }
})

useSeoMeta({ title: 'پیگیری کد خرید | مدیریت لومیا' })
</script>
