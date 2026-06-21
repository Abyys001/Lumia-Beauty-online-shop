<template>
  <div class="container-lumia py-8">
    <h1 class="section-title">سبد خرید</h1>

    <div v-if="cart.loading" class="flex justify-center py-16">
      <span class="loading loading-spinner loading-lg" />
    </div>

    <div v-else-if="!cart.items.length" class="text-center py-16">
      <p class="text-base-content/50 mb-4">سبد خرید شما خالی است</p>
      <NuxtLink to="/shop" class="btn-lumia">مشاهده محصولات</NuxtLink>
    </div>

    <div v-else class="grid lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-4">
        <div
          v-for="item in cart.items"
          :key="item.id"
          class="card-lumia p-4 flex gap-4"
        >
          <img
            v-if="item.product.primary_image"
            :src="item.product.primary_image"
            :alt="item.product.name"
            class="w-20 h-20 rounded-xl object-cover"
          />
          <div class="flex-1">
            <NuxtLink :to="`/shop/${item.product.slug}`" class="font-medium hover:text-primary">
              {{ item.product.name }}
            </NuxtLink>
            <p class="text-primary text-sm mt-1">{{ formatPrice(item.product.price) }}</p>
            <div class="flex items-center gap-2 mt-2">
              <button class="btn btn-xs btn-circle btn-outline" @click="cart.updateItem(item.id, item.quantity - 1)">−</button>
              <span>{{ item.quantity }}</span>
              <button class="btn btn-xs btn-circle btn-outline" @click="cart.updateItem(item.id, item.quantity + 1)">+</button>
              <button class="btn btn-xs btn-ghost text-error mr-auto" @click="cart.removeItem(item.id)">حذف</button>
            </div>
          </div>
          <div class="text-left">
            <p class="font-bold">{{ formatPrice(item.subtotal) }}</p>
          </div>
        </div>
      </div>

      <div class="card-lumia p-6 h-fit sticky top-24">
        <h3 class="font-bold mb-4">خلاصه سفارش</h3>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span>جمع جزء</span>
            <span>{{ formatPrice(cart.total) }}</span>
          </div>
          <div class="flex justify-between text-base-content/50">
            <span>ارسال</span>
            <span>محاسبه در تسویه</span>
          </div>
        </div>
        <div class="divider" />
        <div class="flex justify-between font-bold mb-4">
          <span>جمع کل</span>
          <span class="text-primary">{{ formatPrice(cart.total) }}</span>
        </div>
        <NuxtLink to="/checkout" class="btn btn-primary w-full rounded-full">
          ادامه تسویه حساب
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const cart = useCartStore()
const { formatPrice } = useApi()

onMounted(() => cart.fetchCart())

useSeoMeta({
  title: 'سبد خرید | لومیا بیوتی',
  robots: 'noindex, nofollow',
})
</script>
