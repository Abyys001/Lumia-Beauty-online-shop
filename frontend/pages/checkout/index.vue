<template>
  <div class="container-lumia py-8">
    <h1 class="text-xl sm:text-2xl md:text-3xl font-extrabold text-base-content text-right mb-6 sm:mb-8">تکمیل خرید و تسویه حساب</h1>

    <!-- Not Authenticated State -->
    <CheckoutAuth v-if="!auth.isAuthenticated" @authenticated="onAuthenticated" />

    <!-- Authenticated Checkout Form -->
    <div v-else class="grid lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
      <!-- Right Column: Shipping Address & Coupon Code (col-span-2) -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Address card -->
        <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2 justify-start" style="flex-direction: row-reverse;">
            
            <span>آدرس گیرنده و ارسال</span>
          </h2>
          
          <div v-if="addresses?.length" class="space-y-3 mb-6">
            <p class="text-sm text-base-content/50 mb-2">انتخاب از آدرس‌های قبلی:</p>
            <label
              v-for="addr in addresses"
              :key="addr.id"
              class="flex items-start gap-3 p-4 rounded-2xl border cursor-pointer transition-all hover:bg-base-100/50"
              :class="selectedAddress === addr.id ? 'border-primary bg-primary/5' : 'border-base-200'"
              style="flex-direction: row-reverse;"
            >
              <input v-model="selectedAddress" type="radio" :value="addr.id" class="radio radio-primary mt-1" />
              <div class="flex-1 text-right">
                <p class="font-bold text-sm text-base-content">{{ addr.title }} — گیرنده: {{ addr.receiver_name }}</p>
                <p class="text-xs text-base-content/50 mt-1">{{ addr.province }}، {{ addr.city }}، {{ addr.address_line }} (کد پستی: {{ addr.postal_code }})</p>
              </div>
            </label>
            
            <div class="divider my-4">یا آدرس جدید وارد کنید</div>
          </div>
          
          <!-- Address Fields -->
          <fieldset class="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-5" :disabled="!!selectedAddress">
            <CheckoutField
              id="shipping_name"
              label="نام و نام خانوادگی گیرنده"
              required
              :error="fieldErrors.shipping_name"
            >
              <input
                id="shipping_name"
                v-model="form.shipping_name"
                type="text"
                class="input input-bordered w-full rounded-xl text-right"
                :class="{ 'input-error': fieldErrors.shipping_name }"
                placeholder="مثال: مریم رضایی"
                autocomplete="name"
              />
            </CheckoutField>

            <CheckoutField
              id="shipping_phone"
              label="شماره موبایل گیرنده"
              required
              hint="برای هماهنگی ارسال و پیگیری مرسوله"
              :error="fieldErrors.shipping_phone"
            >
              <input
                id="shipping_phone"
                v-model="form.shipping_phone"
                type="tel"
                inputmode="tel"
                maxlength="11"
                dir="ltr"
                class="input input-bordered w-full rounded-xl text-left"
                :class="{ 'input-error': fieldErrors.shipping_phone }"
                placeholder="09123456789"
                autocomplete="tel"
                @input="form.shipping_phone = toEnDigits(form.shipping_phone).replace(/\D/g, '')"
              />
            </CheckoutField>

            <CheckoutField id="shipping_province" label="استان" required :error="fieldErrors.shipping_province">
              <select
                id="shipping_province"
                v-model="form.shipping_province"
                class="select select-bordered w-full rounded-xl text-right"
                :class="{ 'select-error': fieldErrors.shipping_province }"
                @change="onProvinceChange"
              >
                <option value="" disabled>استان را انتخاب کنید</option>
                <option v-for="(cities, prov) in provincesAndCities" :key="prov" :value="prov">{{ prov }}</option>
              </select>
            </CheckoutField>

            <CheckoutField
              id="shipping_city"
              label="شهر"
              required
              :hint="form.shipping_province ? '' : 'ابتدا استان را انتخاب کنید'"
              :error="fieldErrors.shipping_city"
            >
              <select
                id="shipping_city"
                v-model="form.shipping_city"
                class="select select-bordered w-full rounded-xl text-right"
                :class="{ 'select-error': fieldErrors.shipping_city }"
                :disabled="!form.shipping_province"
              >
                <option value="" disabled>شهر را انتخاب کنید</option>
                <option v-for="city in availableCities" :key="city" :value="city">{{ city }}</option>
              </select>
            </CheckoutField>

            <CheckoutField
              id="shipping_postal_code"
              label="کد پستی"
              required
              hint="۱۰ رقم، بدون خط تیره"
              :error="fieldErrors.shipping_postal_code"
            >
              <input
                id="shipping_postal_code"
                v-model="form.shipping_postal_code"
                type="text"
                inputmode="numeric"
                maxlength="10"
                dir="ltr"
                class="input input-bordered w-full rounded-xl text-left tracking-widest"
                :class="{ 'input-error': fieldErrors.shipping_postal_code }"
                placeholder="1234567890"
                autocomplete="postal-code"
                @input="form.shipping_postal_code = toEnDigits(form.shipping_postal_code).replace(/\D/g, '')"
              />
            </CheckoutField>

            <CheckoutField
              id="shipping_plate_number"
              label="پلاک و واحد"
              hint="اختیاری"
              :error="fieldErrors.shipping_plate_number"
            >
              <input
                id="shipping_plate_number"
                v-model="form.shipping_plate_number"
                type="text"
                dir="ltr"
                class="input input-bordered w-full rounded-xl text-left"
                :class="{ 'input-error': fieldErrors.shipping_plate_number }"
                placeholder="12 — واحد 3"
              />
            </CheckoutField>

            <CheckoutField
              id="shipping_address"
              label="آدرس دقیق پستی"
              required
              class="md:col-span-2"
              hint="خیابان، کوچه و نشانی کامل — بدون نام استان و شهر"
              :error="fieldErrors.shipping_address"
            >
              <textarea
                id="shipping_address"
                v-model="form.shipping_address"
                rows="3"
                class="textarea textarea-bordered w-full rounded-xl text-right leading-7"
                :class="{ 'textarea-error': fieldErrors.shipping_address }"
                placeholder="مثال: خیابان ولیعصر، کوچه شهید احمدی، ساختمان نگین"
                autocomplete="street-address"
              />
            </CheckoutField>

            <label v-if="!selectedAddress" class="flex items-center gap-2 md:col-span-2 cursor-pointer">
              <input v-model="saveNewAddress" type="checkbox" class="checkbox checkbox-primary checkbox-sm" />
              <span class="text-sm">ذخیره این آدرس در دفترچه آدرس‌ها</span>
            </label>
          </fieldset>
        </div>

        <!-- Coupon Card -->
        <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2 justify-start" style="flex-direction: row-reverse;">
            
            <span>کد تخفیف</span>
          </h2>
          <div class="flex gap-2">
            <input v-model="couponCode" class="input input-bordered rounded-xl flex-1 text-right" placeholder="کد تخفیف خود را وارد کنید" />
            <button type="button" class="btn btn-outline rounded-xl px-6 font-bold" @click="validateCoupon">اعمال کد</button>
          </div>
          <p v-if="couponMessage" class="text-sm mt-2 font-bold" :class="couponValid ? 'text-success' : 'text-error'">
            {{ couponMessage }}
          </p>
        </div>
      </div>

      <!-- Left Column: Cart Invoice Summary -->
      <div class="space-y-6">
        <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm sticky top-4">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2 justify-start" style="flex-direction: row-reverse;">
            
            <span>فاکتور پرداخت</span>
          </h2>
          
          <!-- Cart Items list -->
          <div class="max-h-[200px] overflow-y-auto mb-4 space-y-3 pr-1">
            <div v-for="item in cart.items" :key="item.id" class="flex justify-between items-center gap-2 text-sm" style="flex-direction: row-reverse;">
              <div class="flex items-center gap-2" style="flex-direction: row-reverse;">
                <AppImage
                  v-if="item.product?.primary_image"
                  :src="item.product.primary_image"
                  alt=""
                  img-class="w-10 h-10 rounded-lg object-cover"
                />
                <span class="font-medium text-right line-clamp-1 w-[120px]">{{ item.product?.name }}</span>
              </div>
              <div class="text-left font-bold text-base-content/70">
                <span>{{ item.quantity }} ×</span>
                <span class="mr-1">{{ formatPrice(item.product?.price || 0) }}</span>
              </div>
            </div>
          </div>
          
          <div class="divider my-4"></div>

          <div class="space-y-3 text-sm">
            <div class="flex justify-between" style="flex-direction: row-reverse;">
              <span class="text-base-content/60">جمع اقلام ({{ cart.itemCount }} عدد):</span>
              <span class="font-bold">{{ formatPrice(cart.total) }} تومان</span>
            </div>
            <div v-if="discountAmount" class="flex justify-between text-success" style="flex-direction: row-reverse;">
              <span class="text-success/80">تخفیف:</span>
              <span class="font-bold">− {{ formatPrice(discountAmount) }} تومان</span>
            </div>
            <div class="flex justify-between" style="flex-direction: row-reverse;">
              <span class="text-base-content/60">هزینه ارسال پستی:</span>
              <span class="font-bold">{{ formatPrice(shippingCost) }} تومان</span>
            </div>
          </div>
          
          <div class="divider my-4"></div>
          
          <div class="flex justify-between font-black text-lg mb-6" style="flex-direction: row-reverse;">
            <span class="text-primary">مبلغ قابل پرداخت:</span>
            <span class="text-primary text-xl">{{ formatPrice(finalTotal) }} تومان</span>
          </div>
          
          <!-- Everything wrong with the submission, in one place -->
          <div v-if="summary.length" class="rounded-2xl border border-error/30 bg-error/5 p-4 mb-4 text-right" role="alert">
            <p class="flex items-center gap-2 text-sm font-bold text-error mb-2">
              <svg class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              </svg>
              <span>{{ summary.length === 1 ? 'سفارش ثبت نشد' : `سفارش ثبت نشد — ${toFaDigits(summary.length)} مورد را اصلاح کنید` }}</span>
            </p>
            <ul class="space-y-1 text-xs text-error/90 leading-6 list-disc pr-4">
              <li v-for="message in summary" :key="message">{{ message }}</li>
            </ul>
          </div>

          <button @click="submitOrder" type="button" class="btn-lumia w-full py-4 text-center font-bold text-base shadow-lg transition-transform hover:scale-[1.01]" :disabled="submitting || redirecting || cart.itemCount === 0">
            <span v-if="redirecting">در حال آماده‌سازی کد خرید...</span>
            <span v-else-if="submitting" class="loading loading-spinner loading-sm" />
            <span v-else>ثبت سفارش و دریافت کد خرید</span>
          </button>

          <div class="mt-4 rounded-2xl border-r-4 border-lumia-gold bg-lumia-cream/60 p-4 text-right">
            <p class="text-sm font-black text-lumia-dark leading-7">
              پرداخت این فروشگاه کارت به کارت است.
            </p>
            <p class="mt-1 text-xs font-bold text-lumia-dark/70 leading-6">
              پس از ثبت سفارش، یک <span class="text-lumia-gold">کد خرید ۶ رقمی</span> دریافت می‌کنید. آن را از طریق پیامک، تلگرام، واتس‌اپ یا بله برای فروشنده بفرستید تا شماره کارت برای شما ارسال شود. راهنمای کامل در صفحه بعد نمایش داده می‌شود.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Address, Order, ShippingSettings } from '~/types'
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

const auth = useAuthStore()
const cart = useCartStore()
const { apiFetch, formatPrice } = useApi()
const router = useRouter()

const FIELD_LABELS: Record<string, string> = {
  shipping_name: 'نام و نام خانوادگی گیرنده',
  shipping_phone: 'شماره موبایل گیرنده',
  shipping_province: 'استان',
  shipping_city: 'شهر',
  shipping_address: 'آدرس دقیق پستی',
  shipping_postal_code: 'کد پستی',
  shipping_plate_number: 'پلاک و واحد',
  address_id: 'آدرس انتخاب‌شده',
  coupon_code: 'کد تخفیف',
  note: 'یادداشت سفارش',
}

const { fieldErrors, summary, clear: clearErrors, setField, setFromApi } = useFormErrors(FIELD_LABELS)

const selectedAddress = ref('')
const couponCode = ref('')
const couponValid = ref(false)
const couponMessage = ref('')
const discountAmount = ref(0)
const submitting = ref(false)
const redirecting = ref(false)
const saveNewAddress = ref(false)

const form = reactive({
  shipping_name: '',
  shipping_phone: '',
  shipping_province: '',
  shipping_city: '',
  shipping_address: '',
  shipping_postal_code: '',
  shipping_plate_number: '',
  note: '',
})

// Provinces and Major Cities of Iran
const { provincesAndCities } = useIranProvinces()

const availableCities = computed(() => {
  if (!form.shipping_province) return []
  return provincesAndCities[form.shipping_province as keyof typeof provincesAndCities] || []
})

function onProvinceChange() {
  form.shipping_city = ''
}

const { data: addresses } = await useAsyncData('addresses', () =>
  auth.isAuthenticated ? apiFetch<Address[]>('/user/addresses/') : Promise.resolve([]),
)

onMounted(() => cart.fetchCart())

function onAuthenticated() {
  navigateTo('/checkout', { replace: true })
}

const { data: shippingSettings } = await usePublicData(
  'shipping-settings',
  () => apiFetch<ShippingSettings>('/store/shipping/'),
  { default: () => ({ shipping_cost: 150000, free_shipping_threshold: 0 }) },
)

const shippingCost = computed(() => shippingSettings.value?.shipping_cost ?? 150000)

const appliedShippingCost = computed(() => shippingCost.value)

const finalTotal = computed(() =>
  Math.max(cart.total - discountAmount.value + appliedShippingCost.value, 0),
)

async function validateCoupon() {
  if (!couponCode.value) return
  try {
    const result = await apiFetch<{
      valid: boolean
      discount_amount: number
      detail?: string
    }>('/coupons/validate/', {
      method: 'POST',
      body: { code: couponCode.value, subtotal: cart.total },
    })
    couponValid.value = result.valid
    discountAmount.value = result.discount_amount
    couponMessage.value = 'کد تخفیف اعمال شد'
  } catch (e: unknown) {
    couponValid.value = false
    discountAmount.value = 0
    const err = e as { data?: { detail?: string } }
    couponMessage.value = err.data?.detail || 'کد نامعتبر'
  }
}

/**
 * Mirrors the rules in `CreateOrderSerializer` so the customer is told what is
 * wrong before a round trip. The server stays the authority — anything this
 * misses still comes back as a field error and lands in the same slots.
 */
function validateForm(): boolean {
  clearErrors()
  if (selectedAddress.value) return true

  const name = form.shipping_name.trim()
  if (!name) setField('shipping_name', 'نام و نام خانوادگی گیرنده الزامی است.')
  else if (name.length < 3) setField('shipping_name', 'نام گیرنده باید حداقل ۳ حرف باشد.')

  if (!form.shipping_phone) setField('shipping_phone', 'شماره موبایل گیرنده الزامی است.')
  else if (!/^09\d{9}$/.test(form.shipping_phone))
    setField('shipping_phone', 'شماره موبایل باید ۱۱ رقم باشد و با ۰۹ شروع شود. مثال: ۰۹۱۲۳۴۵۶۷۸۹')

  if (!form.shipping_province) setField('shipping_province', 'استان الزامی است.')
  if (!form.shipping_city) setField('shipping_city', 'شهر الزامی است.')

  if (!form.shipping_postal_code) setField('shipping_postal_code', 'کد پستی الزامی است.')
  else if (!/^\d{10}$/.test(form.shipping_postal_code))
    setField('shipping_postal_code', 'کد پستی باید دقیقاً ۱۰ رقم باشد (بدون خط تیره).')

  const address = form.shipping_address.trim()
  if (!address) setField('shipping_address', 'آدرس دقیق پستی الزامی است.')
  else if (address.length < 10)
    setField('shipping_address', 'آدرس را کامل‌تر بنویسید (حداقل ۱۰ حرف) تا بسته درست به دستتان برسد.')

  const firstBadField = Object.keys(FIELD_LABELS).find(field => fieldErrors[field])
  if (firstBadField) {
    focusField(firstBadField)
    return false
  }
  return true
}

function focusField(field: string) {
  nextTick(() => {
    const el = document.getElementById(field)
    el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    ;(el as HTMLElement | null)?.focus?.({ preventScroll: true })
  })
}

async function submitOrder() {
  if (!validateForm()) return
  submitting.value = true
  try {
    const body: Record<string, string> = {
      note: form.note,
      coupon_code: couponCode.value,
    }
    if (selectedAddress.value) {
      body.address_id = selectedAddress.value
    } else {
      Object.assign(body, form)
    }

    const order = await apiFetch<Order>('/orders/', { method: 'POST', body })
    if (saveNewAddress.value && !selectedAddress.value) {
      await apiFetch('/user/addresses/', {
        method: 'POST',
        body: {
          title: 'خانه',
          receiver_name: form.shipping_name || auth.user?.full_name || 'مشتری',
          receiver_phone: form.shipping_phone,
          province: form.shipping_province,
          city: form.shipping_city,
          address_line: form.shipping_address,
          postal_code: form.shipping_postal_code,
          is_default: !addresses.value?.length,
        },
      }).catch(() => {})
    }
    redirecting.value = true
    await navigateTo({ path: '/checkout/pending', query: { order: order.order_number } })
  } catch (e: unknown) {
    redirecting.value = false
    const firstBadField = setFromApi(e, 'ثبت سفارش انجام نشد. لطفاً اطلاعات بالا را بررسی کنید و دوباره تلاش کنید.')
    if (firstBadField) focusField(firstBadField)
  } finally {
    submitting.value = false
  }
}

useSeoMeta({
  title: 'تسویه حساب | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
