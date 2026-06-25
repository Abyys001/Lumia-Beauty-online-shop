<template>
  <section v-if="products?.length" class="mt-12">
    <h2 class="text-xl font-bold text-lumia-dark mb-6">محصولات مرتبط</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        :product="product"
        show-quick-add
        show-wishlist
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Product } from '~/types'

const props = defineProps<{ slug: string }>()
const { apiFetch } = useApi()

const { data: products } = await useAsyncData(
  () => `related-${props.slug}`,
  () => apiFetch<Product[]>(`/products/${props.slug}/related/`),
  { default: () => [] },
)
</script>
