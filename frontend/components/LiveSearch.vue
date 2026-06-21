<template>
  <div class="relative">
    <div class="form-control">
      <input
        v-model="query"
        type="search"
        placeholder="جستجوی محصول..."
        class="input input-bordered input-sm w-40 lg:w-56 rounded-full bg-base-100"
        @focus="showResults = true"
        @blur="onBlur"
      />
    </div>

    <div
      v-if="showResults && (results.length > 0 || loading)"
      class="absolute top-full mt-2 left-0 w-72 bg-base-100 rounded-2xl shadow-xl border border-base-200 z-50 overflow-hidden"
    >
      <div v-if="loading" class="p-4 text-center">
        <span class="loading loading-spinner loading-sm" />
      </div>
      <ul v-else class="max-h-80 overflow-y-auto">
        <li
          v-for="product in results"
          :key="product.id"
        >
          <NuxtLink
            :to="`/shop/${product.slug}`"
            class="flex items-center gap-3 p-3 hover:bg-base-200 transition-colors"
            @click="showResults = false"
          >
            <img
              v-if="product.primary_image"
              :src="product.primary_image"
              :alt="product.name"
              class="w-10 h-10 rounded-lg object-cover"
            />
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ product.name }}</p>
              <p class="text-xs text-primary">{{ formatPrice(product.price) }}</p>
            </div>
          </NuxtLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types'

const { apiFetch, formatPrice } = useApi()
const query = ref('')
const results = ref<Product[]>([])
const loading = ref(false)
const showResults = ref(false)

let debounceTimer: ReturnType<typeof setTimeout>

watch(query, (val) => {
  clearTimeout(debounceTimer)
  if (val.length < 2) {
    results.value = []
    return
  }
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      results.value = await apiFetch<Product[]>('/products/search/', { query: { q: val } })
    } catch {
      results.value = []
    } finally {
      loading.value = false
    }
  }, 300)
})

function onBlur() {
  setTimeout(() => { showResults.value = false }, 200)
}
</script>
