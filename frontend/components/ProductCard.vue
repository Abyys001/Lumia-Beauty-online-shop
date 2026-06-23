<template>
  <NuxtLink :to="`/shop/${product.slug}`" class="card-lumia group block overflow-hidden">
    <figure class="relative aspect-square bg-base-200 overflow-hidden">
      <img
        v-if="product.primary_image"
        :src="imageSrc"
        :alt="product.name"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-base-content/30">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <span
        v-if="product.discount_percent > 0"
        class="absolute top-3 right-3 badge badge-error text-white"
      >
        {{ product.discount_percent }}٪
      </span>
      <button
        v-if="showQuickAdd && product.is_in_stock"
        class="absolute bottom-3 left-3 btn btn-primary btn-sm rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0"
        @click.prevent="quickAdd"
      >
        افزودن به سبد
      </button>
    </figure>
    <div class="card-body p-4">
      <p v-if="product.brand_name" class="text-xs text-base-content/50">{{ product.brand_name }}</p>
      <h3 class="font-semibold text-sm line-clamp-2 group-hover:text-primary transition-colors">
        {{ product.name }}
      </h3>
      <div class="flex items-center gap-2 mt-1">
        <span class="font-bold text-primary">{{ formatPrice(product.price) }}</span>
        <span
          v-if="product.compare_at_price"
          class="text-xs text-base-content/40 line-through"
        >
          {{ formatPrice(product.compare_at_price) }}
        </span>
      </div>
      <span v-if="!product.is_in_stock" class="text-xs text-error mt-1">ناموجود</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Product } from '~/types'
import { useCartStore } from '~/stores/cart'

const props = defineProps<{
  product: Product
  showQuickAdd?: boolean
}>()

const cart = useCartStore()
const { formatPrice } = useApi()
const { normalizeMediaUrl } = useMediaUrl()

const imageSrc = computed(() => normalizeMediaUrl(props.product.primary_image) || props.product.primary_image || '')

async function quickAdd() {
  await cart.addItem(props.product.id)
}
</script>
