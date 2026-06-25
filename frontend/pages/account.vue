<template>
  <div class="container-lumia py-8">
    <div v-if="!auth.isAuthenticated" class="text-center py-16">
      <p class="mb-4">برای مشاهده حساب کاربری وارد شوید.</p>
      <NuxtLink to="/auth" class="btn-lumia">ورود</NuxtLink>
    </div>

    <template v-else>
      <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6 sm:mb-8">
        <div>
          <h1 class="section-title">حساب کاربری</h1>
          <p class="text-base-content/60">{{ auth.user?.full_name || auth.user?.phone }}</p>
        </div>
        <button class="btn btn-outline btn-sm rounded-full" @click="logout">خروج</button>
      </div>

      <div role="tablist" class="tabs tabs-boxed bg-base-200 rounded-full w-full sm:w-fit mb-6 sm:mb-8 overflow-x-auto">
        <button role="tab" class="tab rounded-full" :class="{ 'tab-active': tab === 'orders' }" @click="tab = 'orders'">سفارشات</button>
        <button role="tab" class="tab rounded-full" :class="{ 'tab-active': tab === 'wishlist' }" @click="openWishlistTab">علاقه‌مندی‌ها</button>
        <button role="tab" class="tab rounded-full" :class="{ 'tab-active': tab === 'addresses' }" @click="tab = 'addresses'">آدرس‌ها</button>
        <button role="tab" class="tab rounded-full" :class="{ 'tab-active': tab === 'profile' }" @click="tab = 'profile'">پروفایل</button>
      </div>

      <!-- Orders -->
      <div v-if="tab === 'orders'">
        <div v-if="ordersPending" class="flex justify-center py-8"><span class="loading loading-spinner" /></div>
        <div v-else-if="orders?.length" class="space-y-4">
          <div v-for="order in orders" :key="order.id" class="card-lumia p-4">
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium">{{ order.order_number }}</p>
                <p class="text-sm text-base-content/60">{{ formatDate(order.created_at) }}</p>
              </div>
              <span class="badge" :class="statusBadge(order.status)">{{ order.status_display }}</span>
            </div>
            <div class="mt-2 text-sm">
              <p v-for="item in order.items" :key="item.id" class="text-base-content/70">{{ item.product_name }} × {{ item.quantity }}</p>
            </div>
            <div class="flex justify-between items-center mt-3">
              <p class="font-bold text-primary">{{ formatPrice(order.total) }}</p>
              <NuxtLink :to="`/account/orders/${order.order_number}`" class="btn btn-ghost btn-sm text-primary">مشاهده جزئیات</NuxtLink>
            </div>
          </div>
        </div>
        <p v-else class="text-center text-base-content/50 py-8">سفارشی ثبت نشده است</p>
      </div>

      <!-- Wishlist -->
      <div v-if="tab === 'wishlist'">
        <div v-if="wishlist.loading" class="flex justify-center py-8"><span class="loading loading-spinner" /></div>
        <div v-else-if="wishlist.products.length" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <ProductCard v-for="product in wishlist.products" :key="product.id" :product="product" show-quick-add show-wishlist />
        </div>
        <p v-else class="text-center text-base-content/50 py-8">لیست علاقه‌مندی‌ها خالی است</p>
      </div>

      <!-- Addresses -->
      <div v-if="tab === 'addresses'">
        <div class="flex justify-end mb-4">
          <button class="btn btn-primary btn-sm rounded-full" @click="addressModal?.open()">افزودن آدرس</button>
        </div>
        <div v-if="addresses?.length" class="space-y-3">
          <div v-for="addr in addresses" :key="addr.id" class="card-lumia p-4">
            <div class="flex justify-between items-start gap-2">
              <div>
                <p class="font-medium">{{ addr.title }}</p>
                <p class="text-sm text-base-content/60 mt-1">{{ addr.province }}، {{ addr.city }} — {{ addr.address_line }}</p>
                <p class="text-xs text-base-content/50 mt-1">{{ addr.receiver_name }} — {{ addr.receiver_phone }}</p>
              </div>
              <span v-if="addr.is_default" class="badge badge-primary badge-sm shrink-0">پیش‌فرض</span>
            </div>
            <div class="flex flex-wrap gap-2 mt-3">
              <button class="btn btn-ghost btn-xs" @click="addressModal?.open(addr)">ویرایش</button>
              <button v-if="!addr.is_default" class="btn btn-ghost btn-xs text-primary" @click="setDefault(addr.id)">پیش‌فرض</button>
              <button class="btn btn-ghost btn-xs text-error" @click="deleteAddress(addr.id)">حذف</button>
            </div>
          </div>
        </div>
        <p v-else class="text-center text-base-content/50 py-8">آدرسی ثبت نشده است</p>
        <AccountAddressFormModal ref="addressModal" @saved="refreshAddresses" />
      </div>

      <!-- Profile -->
      <div v-if="tab === 'profile'" class="card-lumia p-6 max-w-full sm:max-w-md">
        <form @submit.prevent="saveProfile">
          <div class="space-y-4">
            <div>
              <label class="label"><span class="label-text">نام</span></label>
              <input v-model="profile.first_name" class="input input-bordered w-full rounded-xl" />
            </div>
            <div>
              <label class="label"><span class="label-text">نام خانوادگی</span></label>
              <input v-model="profile.last_name" class="input input-bordered w-full rounded-xl" />
            </div>
            <div>
              <label class="label"><span class="label-text">ایمیل</span></label>
              <input v-model="profile.email" type="email" class="input input-bordered w-full rounded-xl" dir="ltr" />
            </div>
            <button type="submit" class="btn btn-primary rounded-full" :disabled="saving">ذخیره</button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Address, Order, User } from '~/types'
import { useWishlistStore } from '~/stores/wishlist'

const auth = useAuthStore()
const router = useRouter()
const wishlist = useWishlistStore()
const { apiFetch, formatPrice, formatDate } = useApi()

const tab = ref('orders')
const saving = ref(false)
const addressModal = ref<{ open: (addr?: Address) => void } | null>(null)

const profile = reactive({
  first_name: auth.user?.first_name || '',
  last_name: auth.user?.last_name || '',
  email: auth.user?.email || '',
})

const { data: orders, pending: ordersPending } = await useAsyncData('user-orders', () =>
  auth.isAuthenticated ? apiFetch<Order[]>('/user/orders/') : Promise.resolve([]),
)

const { data: addresses, refresh: refreshAddresses } = await useAsyncData('user-addresses', () =>
  auth.isAuthenticated ? apiFetch<Address[]>('/user/addresses/') : Promise.resolve([]),
)

function openWishlistTab() {
  tab.value = 'wishlist'
  wishlist.loadProducts()
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
  try {
    const updated = await apiFetch<User>('/user/profile/', { method: 'PATCH', body: profile })
    auth.user = updated
    if (import.meta.client) localStorage.setItem('lumia_user', JSON.stringify(updated))
  } finally {
    saving.value = false
  }
}

function logout() {
  wishlist.reset()
  auth.logout()
  router.push('/')
}

useSeoMeta({ title: 'حساب کاربری | لومیا بیوتی', robots: 'noindex, nofollow' })
</script>
