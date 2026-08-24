<template>
  <div class="container-lumia py-6 sm:py-8">
    <AccountShell>
      <template #header>
        <AccountHeader
          :display-name="displayName"
          :phone="auth.user?.phone"
          :first-name="auth.user?.first_name"
          :last-name="auth.user?.last_name"
          @logout="logout"
        />
      </template>

      <template #nav-sidebar>
        <AccountNav :model-value="tab" layout="sidebar" @update:model-value="setTab" />
      </template>

      <template #nav-mobile>
        <AccountNav :model-value="tab" layout="grid" @update:model-value="setTab" />
      </template>

      <!-- Orders -->
      <div v-if="tab === 'orders'" role="tabpanel" aria-label="سفارشات">
        <div v-if="ordersPending" class="flex justify-center py-12">
          <span class="loading loading-spinner loading-lg" />
        </div>
        <div v-else-if="orders?.length" class="space-y-4">
          <div
            v-for="order in orders"
            :key="order.id"
            class="bg-white rounded-3xl border border-base-200 shadow-sm p-4 sm:p-5"
          >
            <div class="flex justify-between items-start gap-3">
              <div class="min-w-0">
                <p class="font-bold text-lumia-dark">{{ order.purchase_code || order.order_number }}</p>
                <p class="text-xs text-base-content/40 font-mono mt-0.5" dir="ltr">{{ order.order_number }}</p>
                <p class="text-sm text-base-content/60 mt-0.5">{{ formatDate(order.created_at) }}</p>
              </div>
              <span class="badge shrink-0" :class="statusBadge(order.status)">{{ order.status_display }}</span>
            </div>
            <p class="text-sm text-base-content/70 mt-3">
              {{ orderItemCount(order) }} قلم — {{ formatPrice(order.total) }}
            </p>
            <div class="mt-2 text-sm text-base-content/60 space-y-0.5">
              <p v-for="(line, i) in orderItemPreview(order)" :key="i">{{ line }}</p>
            </div>
            <NuxtLink
              :to="`/account/orders/${order.order_number}`"
              class="btn btn-primary btn-sm rounded-full w-full sm:w-auto mt-4"
            >
              مشاهده جزئیات
            </NuxtLink>
          </div>
        </div>
        <AccountEmptyState
          v-else
          icon="📦"
          title="سفارشی ثبت نشده است"
          description="اولین خرید خود را از فروشگاه لومیا بیوتی شروع کنید."
          action-label="رفتن به فروشگاه"
          to="/shop"
        />
      </div>

      <!-- Wishlist -->
      <div v-if="tab === 'wishlist'" role="tabpanel" aria-label="علاقه‌مندی‌ها">
        <div v-if="wishlist.loading" class="flex justify-center py-12">
          <span class="loading loading-spinner loading-lg" />
        </div>
        <div v-else-if="wishlist.products.length" class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
          <ProductCard
            v-for="product in wishlist.products"
            :key="product.id"
            :product="product"
            show-quick-add
            show-wishlist
          />
        </div>
        <AccountEmptyState
          v-else
          icon="♡"
          title="لیست علاقه‌مندی‌ها خالی است"
          description="محصولاتی که دوست دارید را با کلیک روی قلب ذخیره کنید."
          action-label="مشاهده محصولات"
          to="/shop"
        />
      </div>

      <!-- Addresses -->
      <div v-if="tab === 'addresses'" role="tabpanel" aria-label="آدرس‌ها">
        <div v-if="addresses?.length" class="space-y-3">
          <div class="flex justify-end mb-1">
            <button class="btn btn-primary btn-sm rounded-full gap-1.5" @click="addressModal?.open()">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              افزودن آدرس
            </button>
          </div>
          <div
            v-for="addr in addresses"
            :key="addr.id"
            class="bg-white rounded-3xl border border-base-200 shadow-sm p-4 sm:p-5"
          >
            <div class="flex justify-between items-start gap-2">
              <div class="flex items-start gap-2 min-w-0">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-primary shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <div class="min-w-0">
                  <p class="font-bold text-lumia-dark">{{ addr.title }}</p>
                  <p class="text-sm text-base-content/60 mt-1">{{ addr.province }}، {{ addr.city }} — {{ addr.address_line }}</p>
                  <p class="text-xs text-base-content/50 mt-1">{{ addr.receiver_name }} — {{ addr.receiver_phone }}</p>
                </div>
              </div>
              <span v-if="addr.is_default" class="badge badge-primary badge-sm shrink-0">پیش‌فرض</span>
            </div>
            <div class="flex flex-wrap gap-2 mt-4">
              <button class="btn btn-ghost btn-sm rounded-full gap-1" @click="addressModal?.open(addr)">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                ویرایش
              </button>
              <button
                v-if="!addr.is_default"
                class="btn btn-ghost btn-sm rounded-full gap-1 text-primary"
                @click="setDefault(addr.id)"
              >
                پیش‌فرض
              </button>
              <button class="btn btn-ghost btn-sm rounded-full gap-1 text-error" @click="deleteAddress(addr.id)">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                حذف
              </button>
            </div>
          </div>
        </div>
        <AccountEmptyState
          v-else
          icon="📍"
          title="آدرسی ثبت نشده است"
          description="برای خرید سریع‌تر، آدرس ارسال خود را اضافه کنید."
          action-label="افزودن اولین آدرس"
          @action="addressModal?.open()"
        />
        <AccountAddressFormModal ref="addressModal" @saved="refreshAddresses" />
      </div>

      <!-- Profile -->
      <div v-if="tab === 'profile'" role="tabpanel" aria-label="پروفایل">
        <div class="bg-white rounded-3xl border border-base-200 shadow-sm p-5 sm:p-6 max-w-lg">
          <h2 class="font-bold text-lg text-lumia-dark mb-4">اطلاعات شخصی</h2>
          <form @submit.prevent="saveProfile">
            <div class="space-y-4">
              <div>
                <label class="label py-1"><span class="label-text">نام</span></label>
                <input v-model="profile.first_name" class="input input-bordered w-full rounded-xl" />
              </div>
              <div>
                <label class="label py-1"><span class="label-text">نام خانوادگی</span></label>
                <input v-model="profile.last_name" class="input input-bordered w-full rounded-xl" />
              </div>
              <div>
                <label class="label py-1"><span class="label-text">شماره موبایل</span></label>
                <input
                  :value="auth.user?.phone"
                  class="input input-bordered w-full rounded-xl bg-base-200"
                  dir="ltr"
                  disabled
                />
              </div>
              <div>
                <label class="label py-1"><span class="label-text">ایمیل</span></label>
                <input v-model="profile.email" type="email" class="input input-bordered w-full rounded-xl" dir="ltr" />
              </div>
              <div v-if="profileSuccess" class="alert alert-success text-sm py-2 rounded-xl">
                تغییرات با موفقیت ذخیره شد.
              </div>
              <div v-if="profileError" class="alert alert-error text-sm py-2 rounded-xl">
                {{ profileError }}
              </div>
              <button type="submit" class="btn btn-primary rounded-full w-full sm:w-auto" :disabled="saving">
                <span v-if="saving" class="loading loading-spinner loading-sm" />
                <span v-else>ذخیره تغییرات</span>
              </button>
            </div>
          </form>
        </div>

        <div class="bg-white rounded-3xl border border-base-200 shadow-sm p-5 sm:p-6 max-w-lg mt-6">
          <h2 class="font-bold text-lg text-lumia-dark mb-1">تغییر رمز عبور</h2>
          <p class="text-xs text-base-content/60 mb-4">رمز جدید را وارد کنید؛ نیازی به رمز فعلی نیست.</p>
          <form @submit.prevent="changePassword">
            <div class="space-y-4">
              <div>
                <label class="label py-1"><span class="label-text">رمز عبور جدید</span></label>
                <UiPasswordInput
                  v-model="passwordForm.new_password"
                  :input-class="passwordErrors.confirm ? 'input-error' : ''"
                  autocomplete="new-password"
                />
              </div>
              <div>
                <label class="label py-1"><span class="label-text">تکرار رمز عبور جدید</span></label>
                <UiPasswordInput
                  v-model="passwordForm.confirm_password"
                  :input-class="passwordErrors.confirm ? 'input-error' : ''"
                  autocomplete="new-password"
                />
                <p v-if="passwordErrors.confirm" class="text-error text-xs mt-1.5 pr-1">{{ passwordErrors.confirm }}</p>
              </div>
              <div v-if="passwordSuccess" class="alert alert-success text-sm py-2 rounded-xl">
                {{ passwordSuccess }}
              </div>
              <div v-if="passwordError" class="alert alert-error text-sm py-2 rounded-xl">
                {{ passwordError }}
              </div>
              <button type="submit" class="btn btn-outline rounded-full w-full sm:w-auto" :disabled="changingPassword">
                <span v-if="changingPassword" class="loading loading-spinner loading-sm" />
                <span v-else>تغییر رمز عبور</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </AccountShell>
  </div>
</template>

<script setup lang="ts">
import type { AccountTab } from '~/components/account/AccountNav.vue'
import type { Address, Order, User } from '~/types'
import { useWishlistStore } from '~/stores/wishlist'

const VALID_TABS: AccountTab[] = ['orders', 'wishlist', 'addresses', 'profile']

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const wishlist = useWishlistStore()
const { apiFetch, formatPrice, formatDate } = useApi()

const saving = ref(false)
const profileSuccess = ref(false)
const profileError = ref('')
const addressModal = ref<{ open: (addr?: Address) => void } | null>(null)

const changingPassword = ref(false)
const passwordSuccess = ref('')
const passwordError = ref('')
const passwordErrors = reactive<{ confirm: string }>({ confirm: '' })
const passwordForm = reactive({ new_password: '', confirm_password: '' })

let profileSuccessTimer: ReturnType<typeof setTimeout> | undefined

const profile = reactive({
  first_name: auth.user?.first_name || '',
  last_name: auth.user?.last_name || '',
  email: auth.user?.email || '',
})

function parseTab(query: unknown): AccountTab {
  const value = String(query || 'orders')
  return VALID_TABS.includes(value as AccountTab) ? value as AccountTab : 'orders'
}

const tab = ref<AccountTab>(parseTab(route.query.tab))

watch(() => route.query.tab, (query) => {
  const next = parseTab(query)
  tab.value = next
  if (next === 'wishlist') wishlist.loadProducts()
})

function setTab(next: AccountTab) {
  tab.value = next
  if (next === 'wishlist') wishlist.loadProducts()
  router.replace({ path: '/account', query: { tab: next } })
}

const displayName = computed(() => {
  const user = auth.user
  if (user?.first_name || user?.last_name) {
    return [user.first_name, user.last_name].filter(Boolean).join(' ')
  }
  return user?.full_name || 'کاربر لومیا'
})

const { data: orders, pending: ordersPending } = await useAsyncData('user-orders', () =>
  auth.isAuthenticated ? apiFetch<Order[]>('/user/orders/') : Promise.resolve([]),
  { server: false },
)

const { data: addresses, refresh: refreshAddresses } = await useAsyncData('user-addresses', () =>
  auth.isAuthenticated ? apiFetch<Address[]>('/user/addresses/') : Promise.resolve([]),
  { server: false },
)

function orderItemCount(order: Order) {
  return order.items.reduce((sum, item) => sum + item.quantity, 0)
}

function orderItemPreview(order: Order) {
  const max = 2
  const lines = order.items.slice(0, max).map(item => `${item.product_name} × ${item.quantity}`)
  const rest = order.items.length - max
  if (rest > 0) lines.push(`و ${rest} مورد دیگر`)
  return lines
}

function statusBadge(status: string) {
  const map: Record<string, string> = {
    paid: 'badge-success', pending: 'badge-warning', shipped: 'badge-info',
    delivered: 'badge-success', cancelled: 'badge-error', processing: 'badge-info',
  }
  return map[status] || 'badge-ghost'
}

async function setDefault(id: string) {
  await apiFetch(`/user/addresses/${id}/`, { method: 'PATCH', body: { is_default: true } })
  await refreshAddresses()
}

async function deleteAddress(id: string) {
  if (!confirm('این آدرس حذف شود؟')) return
  await apiFetch(`/user/addresses/${id}/`, { method: 'DELETE' })
  await refreshAddresses()
}

async function saveProfile() {
  saving.value = true
  profileSuccess.value = false
  profileError.value = ''
  try {
    const updated = await apiFetch<User>('/user/profile/', { method: 'PATCH', body: profile })
    auth.user = updated
    if (import.meta.client) localStorage.setItem('lumia_user', JSON.stringify(updated))
    profileSuccess.value = true
    if (import.meta.client) {
      clearTimeout(profileSuccessTimer)
      profileSuccessTimer = setTimeout(() => {
        profileSuccess.value = false
      }, 4000)
    }
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    profileError.value = err.data?.detail || 'ذخیره تغییرات انجام نشد. دوباره تلاش کنید.'
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  passwordSuccess.value = ''
  passwordError.value = ''
  passwordErrors.confirm = ''

  if (passwordForm.new_password.length < 4) {
    passwordErrors.confirm = 'رمز عبور باید حداقل ۴ کاراکتر باشد'
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordErrors.confirm = 'رمزها یکسان نیستند'
    return
  }

  changingPassword.value = true
  try {
    const res = await apiFetch<{ detail: string }>('/user/password/', { method: 'POST', body: { ...passwordForm } })
    passwordSuccess.value = res.detail || 'رمز عبور با موفقیت تغییر کرد'
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
  } catch (e: unknown) {
    const err = e as { data?: Record<string, string | string[]>; statusCode?: number }
    const first = (field: string) => {
      const v = err.data?.[field]
      return Array.isArray(v) ? v[0] : v
    }
    passwordErrors.confirm = first('confirm_password') || ''
    passwordError.value = first('new_password') || err.data?.detail as string || 'تغییر رمز عبور انجام نشد. دوباره تلاش کنید.'
  } finally {
    changingPassword.value = false
  }
}

function logout() {
  wishlist.reset()
  auth.logout()
  router.push('/')
}

onMounted(() => {
  if (tab.value === 'wishlist') wishlist.loadProducts()
})

onUnmounted(() => {
  clearTimeout(profileSuccessTimer)
})

useSeoMeta({ title: 'حساب کاربری | لومیا بیوتی', robots: 'noindex, nofollow' })
</script>
