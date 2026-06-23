<template>
  <div class="relative">
    <!-- Desktop: inline input (hidden on mobile) -->
    <div class="hidden sm:block form-control">
      <input
        v-model="query"
        type="search"
        placeholder="جستجوی محصول..."
        class="input input-bordered input-sm w-40 lg:w-56 rounded-full bg-base-100"
        @focus="showResults = true"
        @blur="onBlur"
      />
    </div>

    <!-- Mobile: search icon button -->
    <button
      type="button"
      class="sm:hidden btn btn-ghost btn-circle"
      @click="openMobileSearch"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </button>

    <!-- Mobile: full-width search overlay -->
    <div
      v-if="mobileSearchOpen"
      class="sm:hidden fixed inset-x-0 top-16 z-50 bg-base-100 border-b border-base-200 shadow-lg px-4 py-3"
    >
      <div class="flex items-center gap-2">
        <input
          ref="mobileInput"
          v-model="query"
          type="search"
          placeholder="جستجوی محصول..."
          class="input input-bordered input-sm flex-1 rounded-full bg-base-100"
          @focus="showResults = true"
          @blur="onMobileBlur"
        />
        <button type="button" class="btn btn-ghost btn-sm btn-circle" @click="closeMobileSearch">✕</button>
      </div>
      <div v-if="showResults && (results.length > 0 || loading)" class="mt-2 bg-base-100 rounded-2xl border border-base-200 overflow-hidden">
        <div v-if="loading" class="p-4 text-center">
          <span class="loading loading-spinner loading-sm" />
        </div>
        <ul v-else class="max-h-60 overflow-y-auto">
          <li v-for="product in results" :key="product.id">
            <NuxtLink
              :to="`/shop/${product.slug}`"
              class="flex items-center gap-3 p-3 hover:bg-base-200 transition-colors"
              @click="closeMobileSearch"
            >
              <img v-if="product.primary_image" :src="product.primary_image" :alt="product.name" class="w-10 h-10 rounded-lg object-cover" />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ product.name }}</p>
                <p class="text-xs text-primary">{{ formatPrice(product.price) }}</p>
              </div>
            </NuxtLink>
          </li>
        </ul>
      </div>
    </div>

    <!-- Desktop: results dropdown -->
    <div
      v-if="!mobileSearchOpen && showResults && (results.length > 0 || loading)"
      class="hidden sm:block absolute top-full mt-2 start-0 w-full sm:w-80 bg-base-100 rounded-2xl shadow-xl border border-base-200 z-50 overflow-hidden"
    >
      <div v-if="loading" class="p-4 text-center">
        <span class="loading loading-spinner loading-sm" />
      </div>
      <ul v-else class="max-h-80 overflow-y-auto">
        <li v-for="product in results" :key="product.id">
          <NuxtLink
            :to="`/shop/${product.slug}`"
            class="flex items-center gap-3 p-3 hover:bg-base-200 transition-colors"
            @click="showResults = false"
          >
            <img v-if="product.primary_image" :src="product.primary_image" :alt="product.name" class="w-10 h-10 rounded-lg object-cover" />
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
const mobileSearchOpen = ref(false)
const mobileInput = ref<HTMLInputElement | null>(null)

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

async function openMobileSearch() {
  mobileSearchOpen.value = true
  await nextTick()
  mobileInput.value?.focus()
}

function closeMobileSearch() {
  mobileSearchOpen.value = false
  showResults.value = false
  query.value = ''
  results.value = []
}

function onMobileBlur() {
  setTimeout(() => { showResults.value = false }, 200)
}
</script>
