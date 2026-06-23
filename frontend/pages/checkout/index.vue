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
            <i class="fas fa-map-marker-alt text-primary"></i>
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
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input v-model="form.shipping_name" class="input input-bordered rounded-xl text-right" placeholder="نام گیرنده (اختیاری)" :disabled="!!selectedAddress" />
            <input v-model="form.shipping_phone" class="input input-bordered rounded-xl text-right" placeholder="شماره موبایل گیرنده" :disabled="!!selectedAddress" :required="!selectedAddress" />
            
            <!-- Province Dropdown -->
            <select v-model="form.shipping_province" class="select select-bordered rounded-xl text-right" @change="onProvinceChange" :disabled="!!selectedAddress" :required="!selectedAddress">
              <option value="" disabled selected>استان</option>
              <option v-for="(cities, prov) in provincesAndCities" :key="prov" :value="prov">{{ prov }}</option>
            </select>

            <!-- City Dropdown -->
            <select v-model="form.shipping_city" class="select select-bordered rounded-xl text-right" :disabled="!form.shipping_province || !!selectedAddress" :required="!selectedAddress">
              <option value="" disabled selected>شهر</option>
              <option v-for="city in availableCities" :key="city" :value="city">{{ city }}</option>
            </select>
            
            <input v-model="form.shipping_postal_code" class="input input-bordered rounded-xl text-right" placeholder="کد پستی (اختیاری)" :disabled="!!selectedAddress" />
            <textarea v-model="form.shipping_address" class="textarea textarea-bordered rounded-xl md:col-span-2 text-right" placeholder="آدرس دقیق پستی، پلاک و واحد" :disabled="!!selectedAddress" :required="!selectedAddress" />
          </div>
        </div>

        <!-- Coupon Card -->
        <div class="bg-base-100 p-6 rounded-3xl border border-base-200 text-right shadow-sm">
          <h2 class="text-xl font-bold mb-4 flex items-center gap-2 justify-start" style="flex-direction: row-reverse;">
            <i class="fas fa-percent text-primary"></i>
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
            <i class="fas fa-receipt text-primary"></i>
            <span>فاکتور پرداخت</span>
          </h2>
          
          <!-- Cart Items list -->
          <div class="max-h-[200px] overflow-y-auto mb-4 space-y-3 pr-1">
            <div v-for="item in cart.items" :key="item.id" class="flex justify-between items-center gap-2 text-sm" style="flex-direction: row-reverse;">
              <div class="flex items-center gap-2" style="flex-direction: row-reverse;">
                <img v-if="item.product?.primary_image" :src="item.product.primary_image" class="w-10 h-10 rounded-lg object-cover" />
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
              <span class="font-bold">{{ freeShipping || cart.total >= 500000 ? 'رایگان' : formatPrice(50000) + ' تومان' }}</span>
            </div>
          </div>
          
          <div class="divider my-4"></div>
          
          <div class="flex justify-between font-black text-lg mb-6" style="flex-direction: row-reverse;">
            <span class="text-primary">مبلغ قابل پرداخت:</span>
            <span class="text-primary text-xl">{{ formatPrice(finalTotal) }} تومان</span>
          </div>
          
          <button @click="submitOrder" type="button" class="btn-lumia w-full py-4 text-center font-bold text-base shadow-lg transition-transform hover:scale-[1.01]" :disabled="submitting || cart.itemCount === 0">
            <span v-if="submitting" class="loading loading-spinner loading-sm" />
            <span v-else><i class="fas fa-lock ml-2"></i> پرداخت امن با زرین‌پال</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Address, Order } from '~/types'
import { useAuthStore } from '~/stores/auth'
import { useCartStore } from '~/stores/cart'

const auth = useAuthStore()
const cart = useCartStore()
const { apiFetch, formatPrice } = useApi()
const router = useRouter()

const selectedAddress = ref('')
const couponCode = ref('')
const couponValid = ref(false)
const couponMessage = ref('')
const discountAmount = ref(0)
const freeShipping = ref(false)
const submitting = ref(false)

const form = reactive({
  shipping_name: '',
  shipping_phone: '',
  shipping_province: '',
  shipping_city: '',
  shipping_address: '',
  shipping_postal_code: '',
  note: '',
})

// Provinces and Major Cities of Iran
const provincesAndCities = {
  'تهران': ['تهران', 'ری', 'تجریش', 'ورامین', 'اسلامشهر', 'شهریار', 'قدس', 'دماوند', 'فیروزکوه'],
  'اصفهان': ['اصفهان', 'کاشان', 'خمینی‌شهر', 'نجف‌آباد', 'شاهین‌شهر', 'شهرضا', 'فولادشهر'],
  'فارس': ['شیراز', 'مرودشت', 'جهرم', 'فسا', 'کازرون', 'لارستان', 'فیروزآباد'],
  'خراسان رضوی': ['مشهد', 'نیشابور', 'سبزوار', 'تربت حیدریه', 'قوچان', 'کاشمر', 'گناباد'],
  'آذربایجان شرقی': ['تبریز', 'مراغه', 'مرند', 'میانه', 'اهر', 'بناب', 'سراب'],
  'مازندران': ['ساری', 'بابل', 'آمل', 'قائم‌شهر', 'تنکابن', 'چالوس', 'بابلسر', 'نوشهر'],
  'گیلان': ['رشت', 'بندر انزلی', 'لاهیجان', 'لنگرود', 'تالش', 'رودسر', 'فومن'],
  'البرز': ['کرج', 'فردیس', 'کمال‌شهر', 'نظرآباد', 'هشتگرد', 'طالقان'],
  'خوزستان': ['اهواز', 'دزفول', 'آبادان', 'خرمشهر', 'اندیمشک', 'ایذه', 'ماهشهر'],
  'یزد': ['یزد', 'میبد', 'اردکان', 'بافق', 'ابرکوه', 'تفت'],
  'کرمان': ['کرمان', 'سیرجان', 'رفسنجان', 'جیرفت', 'بم', 'زرند', 'کهنوج']
}

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

const finalTotal = computed(() => {
  const shipping = freeShipping.value || cart.total >= 500000 ? 0 : 50000
  return Math.max(cart.total - discountAmount.value + shipping, 0)
})

async function validateCoupon() {
  if (!couponCode.value) return
  try {
    const result = await apiFetch<{
      valid: boolean
      discount_amount: number
      free_shipping: boolean
      detail?: string
    }>('/coupons/validate/', {
      method: 'POST',
      body: { code: couponCode.value, subtotal: cart.total },
    })
    couponValid.value = result.valid
    discountAmount.value = result.discount_amount
    freeShipping.value = result.free_shipping
    couponMessage.value = 'کد تخفیف اعمال شد'
  } catch (e: unknown) {
    couponValid.value = false
    discountAmount.value = 0
    freeShipping.value = false
    const err = e as { data?: { detail?: string } }
    couponMessage.value = err.data?.detail || 'کد نامعتبر'
  }
}

async function submitOrder() {
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
    const payment = await apiFetch<{ redirect_url: string }>('/payments/zarinpal/request/', {
      method: 'POST',
      body: { order_number: order.order_number },
    })
    
    // Redirect to the sandbox or gateway payment url
    window.location.href = payment.redirect_url
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    alert(err.data?.detail || 'خطا در ثبت سفارش')
  } finally {
    submitting.value = false
  }
}

useSeoMeta({
  title: 'تسویه حساب | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
