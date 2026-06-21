<template>
  <div class="py-12 bg-lumia-light/30">
    <div class="container-lumia">
      <!-- Page Title -->
      <div class="text-center max-w-xl mx-auto mb-10">
        <h1 class="text-3xl font-bold text-lumia-dark">گالری محصولات لومیا بیوتی</h1>
        <div class="w-16 h-0.5 bg-lumia-gold mx-auto my-3"></div>
        <p class="text-sm text-base-content/65">
          مجموعه‌ای از اصیل‌ترین برندهای آرایشی، بهداشتی و خوش‌بوکننده لوکس جهان
        </p>
      </div>

      <!-- Layout Grid -->
      <div class="flex flex-col lg:flex-row gap-8 items-start">
        
        <!-- Mobile Filters Trigger & active tags -->
        <div class="w-full lg:hidden flex flex-col gap-3">
          <button 
            class="btn btn-outline border-lumia-cream hover:bg-lumia-cream/20 hover:text-lumia-dark rounded-full w-full flex items-center justify-center gap-2"
            @click="mobileFiltersOpen = true"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span>فیلترهای پیشرفته و دسته‌بندی</span>
          </button>
        </div>

        <!-- Desktop Sidebar (Hidden on mobile) -->
        <div class="hidden lg:block w-72 shrink-0">
          <FilterSidebar
            :filters="filters"
            :categories="categoriesData?.results || []"
            @update="setFilter"
            @reset="resetFilters"
          />
        </div>

        <!-- Product Gallery Area -->
        <div class="flex-1 w-full space-y-6">
          <!-- Active Filters Bar & Total Count -->
          <div class="flex flex-wrap items-center justify-between gap-4 p-4 bg-white rounded-2xl border border-lumia-cream/80 shadow-xs">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-semibold text-lumia-dark ml-2">فیلترهای فعال:</span>
              <span v-if="activeFiltersCount === 0" class="text-xs text-base-content/50">هیچ فیلتری اعمال نشده است</span>
              
              <!-- Tag Pills -->
              <span 
                v-for="(val, key) in activeFiltersList" 
                :key="key" 
                class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-lumia-cream/40 border border-lumia-gold/10 text-xs text-lumia-dark hover:bg-lumia-cream transition-colors cursor-pointer"
                @click="removeFilter(key)"
              >
                <span>{{ getFilterLabel(key, val) }}</span>
                <span class="text-lumia-gold font-bold">✕</span>
              </span>
            </div>
            
            <div class="text-xs font-semibold text-base-content/70">
              {{ data?.count || 0 }} محصول پیدا شد
            </div>
          </div>

          <!-- Product Cards Grid -->
          <div v-if="pending" class="grid grid-cols-2 lg:grid-cols-3 gap-6">
            <div v-for="i in 6" :key="i" class="skeleton h-80 rounded-3xl" />
          </div>

          <div v-else-if="!data?.results || data.results.length === 0" class="flex flex-col items-center justify-center py-20 bg-white rounded-3xl border border-lumia-cream shadow-xs text-center space-y-4">
            <span class="text-5xl">🔍</span>
            <h3 class="font-bold text-lg text-lumia-dark">محصولی با فیلترهای مورد نظر پیدا نشد</h3>
            <p class="text-sm text-base-content/60">می‌توانید فیلترها را تغییر داده یا از دکمه «پاک کردن همه» استفاده کنید.</p>
            <button class="btn btn-primary rounded-full px-8" @click="resetFilters">پاک کردن همه فیلترها</button>
          </div>

          <div v-else class="space-y-8">
            <div class="grid grid-cols-2 lg:grid-cols-3 gap-6">
              <ProductCard 
                v-for="product in data.results" 
                :key="product.id" 
                :product="product"
                show-quick-add
              />
            </div>

            <!-- Pagination Control -->
            <div v-if="hasPages" class="flex justify-center items-center gap-2 pt-6">
              <button 
                class="btn btn-sm btn-outline border-lumia-cream rounded-full px-4" 
                :disabled="!data.previous"
                @click="changePage(currentPage - 1)"
              >
                قبلی
              </button>
              <span class="text-xs font-semibold text-lumia-dark">
                صفحه {{ currentPage }} از {{ totalPages }}
              </span>
              <button 
                class="btn btn-sm btn-outline border-lumia-cream rounded-full px-4" 
                :disabled="!data.next"
                @click="changePage(currentPage + 1)"
              >
                بعدی
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Mobile Filters Slide-out Overlay Drawer -->
    <div 
      v-if="mobileFiltersOpen" 
      class="fixed inset-0 z-50 lg:hidden bg-lumia-dark/40 backdrop-blur-xs flex justify-end"
      @click.self="mobileFiltersOpen = false"
    >
      <div class="w-80 h-full bg-white p-6 overflow-y-auto flex flex-col justify-between shadow-2xl animate-slide-left">
        <div class="space-y-6">
          <div class="flex items-center justify-between pb-3 border-b border-lumia-cream">
            <h3 class="font-bold text-lg text-lumia-dark">فیلترهای محصولات</h3>
            <button class="text-xl text-base-content/60" @click="mobileFiltersOpen = false">✕</button>
          </div>
          <FilterSidebar
            :filters="filters"
            :categories="categoriesData?.results || []"
            @update="setFilter"
            @reset="resetFilters"
          />
        </div>
        <button 
          class="btn btn-primary rounded-full w-full mt-6"
          @click="mobileFiltersOpen = false"
        >
          اعمال فیلترها
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product, Category, PaginatedResponse } from '~/types'

const route = useRoute()
const router = useRouter()
const { apiFetch } = useApi()

const mobileFiltersOpen = ref(false)
const currentPage = ref(1)

// Filters State
const filters = ref<Record<string, string>>({
  category: (route.query.category as string) || '',
  brand: (route.query.brand as string) || '',
  min_price: (route.query.min_price as string) || '',
  max_price: (route.query.max_price as string) || '',
  scent: (route.query.scent as string) || '',
  skin_type: (route.query.skin_type as string) || '',
  in_stock: (route.query.in_stock as string) || '',
})

// Update local state if URL changes
watch(() => route.query, (newQuery) => {
  filters.value = {
    category: (newQuery.category as string) || '',
    brand: (newQuery.brand as string) || '',
    min_price: (newQuery.min_price as string) || '',
    max_price: (newQuery.max_price as string) || '',
    scent: (newQuery.scent as string) || '',
    skin_type: (newQuery.skin_type as string) || '',
    in_stock: (newQuery.in_stock as string) || '',
  }
  currentPage.value = Number(newQuery.page) || 1
})

// Query Params for API Fetch
const queryParams = computed(() => {
  const params: Record<string, any> = {
    page: currentPage.value,
  }
  for (const [key, val] of Object.entries(filters.value)) {
    if (val) params[key] = val
  }
  return params
})

// Categories fetch
const { data: categoriesData } = await useAsyncData('categories', () =>
  apiFetch<PaginatedResponse<Category>>('/categories/'),
)

// Products fetch
const { data, pending } = await useAsyncData(
  'products',
  () => apiFetch<PaginatedResponse<Product>>('/products/', { query: queryParams.value }),
  { watch: [queryParams] },
)

const totalPages = computed(() => {
  if (!data.value) return 1
  return Math.max(1, Math.ceil(data.value.count / 12)) // Assumes API page size of 12
})
const hasPages = computed(() => totalPages.value > 1)

function setFilter(key: string, value: string) {
  currentPage.value = 1
  filters.value[key] = value
  updateRouterQuery()
}

function removeFilter(key: string) {
  currentPage.value = 1
  filters.value[key] = ''
  updateRouterQuery()
}

function resetFilters() {
  currentPage.value = 1
  for (const key of Object.keys(filters.value)) {
    filters.value[key] = ''
  }
  updateRouterQuery()
}

function changePage(page: number) {
  currentPage.value = page
  updateRouterQuery()
}

function updateRouterQuery() {
  const query: Record<string, any> = {}
  if (currentPage.value > 1) query.page = currentPage.value
  
  for (const [key, val] of Object.entries(filters.value)) {
    if (val) query[key] = val
  }
  router.push({ query })
}

// Active filters computations
const activeFiltersList = computed(() => {
  const list: Record<string, string> = {}
  for (const [key, val] of Object.entries(filters.value)) {
    if (val) list[key] = val
  }
  return list
})

const activeFiltersCount = computed(() => {
  return Object.keys(activeFiltersList.value).length
})

// Human readable labels for active filters
function getFilterLabel(key: string, val: string) {
  const labels: Record<string, string> = {
    category: 'دسته: ' + val,
    brand: 'برند: ' + val,
    min_price: 'حداقل قیمت: ' + Number(val).toLocaleString() + ' تومان',
    max_price: 'حداکثر قیمت: ' + Number(val).toLocaleString() + ' تومان',
    scent: 'رایحه: ' + val,
    skin_type: 'پوست: ' + val,
    in_stock: 'موجود در انبار',
  }
  return labels[key] || `${key}: ${val}`
}

useSeoMeta({
  title: 'خرید عطر نیش، ادکلن اصل و مراقبت پوست | فروشگاه لومیا بیوتی',
  description: 'خرید اینترنتی انواع عطر نیش، ادکلن اصل، آبرسان و محصولات مراقبت از پوست ضد حساسیت و اورجینال با تضمین اصالت و ارسال سریع.',
  ogTitle: 'فروشگاه عطر نیش و لوازم آرایشی لومیا بیوتی',
  ogDescription: 'محصولات اورجینال بهداشتی و عطر خود را با فیلترهای پیشرفته بر اساس طبع، برند و روتین پوست انتخاب کنید.',
})

useSchemaOrg([
  defineBreadcrumb({
    itemListElement: [
      { name: 'خانه', item: '/' },
      { name: 'فروشگاه', item: '/shop' },
    ],
  }),
])
</script>

<style scoped>
.animate-slide-left {
  animation: slideLeft 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideLeft {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}
</style>
