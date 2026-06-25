<template>
  <section class="py-16 md:py-24 bg-white border-y border-lumia-cream">
    <div class="container-lumia">
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-12">
        <div class="text-right">
          <h2 class="section-title text-3xl font-bold">پرفروش‌ترین و محبوب‌ترین‌ها</h2>
          <div class="w-20 h-0.5 bg-lumia-gold my-3" />
          <p class="section-subtitle mb-0 text-sm text-base-content/70">محبوب‌ترین انتخاب‌های همراهان لومیا بیوتی</p>
        </div>
        <NuxtLink to="/shop" class="btn btn-ghost text-lumia-gold hover:bg-lumia-cream/30 rounded-full mt-4 md:mt-0">
          مشاهده کل کاتالوگ ←
        </NuxtLink>
      </div>

      <div v-if="pending" class="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="skeleton h-80 rounded-3xl" />
      </div>

      <div v-else-if="!products.length" class="text-center py-12 bg-lumia-cream/20 rounded-3xl border border-lumia-cream">
        <p class="text-base-content/60 mb-4">در حال حاضر محصولی برای نمایش وجود ندارد.</p>
        <NuxtLink to="/shop" class="btn btn-primary rounded-full">مشاهده فروشگاه</NuxtLink>
      </div>

      <div v-else class="relative group overflow-hidden min-w-0">
        <div class="flex gap-6 overflow-x-auto min-w-0 pb-6 scrollbar-hide snap-x scroll-smooth -mx-4 px-4 md:mx-0 md:px-0">
          <div
            v-for="product in products"
            :key="product.id"
            class="w-[260px] sm:w-[280px] shrink-0 snap-start"
          >
            <ProductCard :product="product" show-quick-add />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Product } from '~/types'

defineProps<{
  products: Product[]
  pending?: boolean
}>()
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
