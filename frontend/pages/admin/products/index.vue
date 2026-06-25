<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-wrap gap-3 mb-5">
      <input
        v-model="search"
        type="text"
        placeholder="جستجو در محصولات..."
        class="input input-bordered input-sm flex-1 min-w-0"
        @input="debouncedFetch"
      />
      <select v-model="filterActive" class="select select-bordered select-sm" @change="fetchProducts">
        <option value="">همه</option>
        <option value="true">فعال</option>
        <option value="false">غیرفعال</option>
      </select>
      <select v-model="filterFeatured" class="select select-bordered select-sm" @change="fetchProducts">
        <option value="">همه محصولات</option>
        <option value="true">ویژه</option>
      </select>
      <NuxtLink to="/admin/products/new" class="btn btn-primary btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        محصول جدید
      </NuxtLink>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div
          v-for="product in products"
          :key="product.id"
          class="bg-white rounded-xl p-3 border border-base-200 flex gap-3"
        >
          <div class="w-14 h-14 rounded-lg overflow-hidden bg-base-200 flex-shrink-0">
            <img v-if="product.primary_image" :src="product.primary_image" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full flex items-center justify-center text-lumia-dark/20">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm truncate">{{ product.name }}</div>
            <div class="text-xs text-lumia-dark/40">{{ product.sku }} · {{ product.category_name }}</div>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-sm font-bold text-lumia-gold">{{ formatPrice(product.price) }}</span>
              <span :class="product.stock < 5 ? 'text-error font-bold' : 'text-lumia-dark/50'" class="text-xs">موجودی: {{ product.stock }}</span>
            </div>
            <div class="flex items-center gap-3 mt-2">
              <label class="flex items-center gap-1 text-xs text-lumia-dark/50 cursor-pointer">
                <input type="checkbox" class="toggle toggle-success toggle-xs" :checked="product.is_active" @change="toggleField(product, 'is_active', $event)" />
                فعال
              </label>
              <label class="flex items-center gap-1 text-xs text-lumia-dark/50 cursor-pointer">
                <input type="checkbox" class="toggle toggle-warning toggle-xs" :checked="product.is_featured" @change="toggleField(product, 'is_featured', $event)" />
                ویژه
              </label>
              <NuxtLink :to="`/admin/products/${product.id}`" class="btn btn-ghost btn-xs text-lumia-gold mr-auto">ویرایش</NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">تصویر</th>
                <th class="font-medium text-right">نام محصول</th>
                <th class="font-medium text-right">دسته‌بندی</th>
                <th class="font-medium text-right">قیمت</th>
                <th class="font-medium text-right">موجودی</th>
                <th class="font-medium text-right">فعال</th>
                <th class="font-medium text-right">ویژه</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in products" :key="product.id" class="hover:bg-base-200/30 transition-colors">
                <td>
                  <div class="w-10 h-10 rounded-lg overflow-hidden bg-base-200">
                    <img v-if="product.primary_image" :src="product.primary_image" class="w-full h-full object-cover" />
                    <div v-else class="w-full h-full flex items-center justify-center text-lumia-dark/20">
                      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="text-sm font-medium">{{ product.name }}</div>
                  <div class="text-xs text-lumia-dark/40">{{ product.sku }}</div>
                </td>
                <td class="text-sm text-lumia-dark/60">{{ product.category_name }}</td>
                <td class="text-sm font-bold">{{ formatPrice(product.price) }}</td>
                <td>
                  <span :class="product.stock < 5 ? 'text-error font-bold' : 'text-lumia-dark/60'" class="text-sm">{{ product.stock }}</span>
                </td>
                <td><input type="checkbox" class="toggle toggle-success toggle-sm" :checked="product.is_active" @change="toggleField(product, 'is_active', $event)" /></td>
                <td><input type="checkbox" class="toggle toggle-warning toggle-sm" :checked="product.is_featured" @change="toggleField(product, 'is_featured', $event)" /></td>
                <td><NuxtLink :to="`/admin/products/${product.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalCount > 0" class="mt-3 px-2 py-3 flex items-center justify-between">
        <span class="text-sm text-lumia-dark/50">{{ totalCount }} محصول</span>
        <div class="flex gap-2">
          <button class="btn btn-ghost btn-sm" :disabled="!prevPage" @click="goToPage(currentPage - 1)">قبلی</button>
          <span class="btn btn-ghost btn-sm pointer-events-none">{{ currentPage }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="!nextPage" @click="goToPage(currentPage + 1)">بعدی</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatPrice } = useApi()

const search = ref('')
const filterActive = ref('')
const filterFeatured = ref('')
const products = ref<any[]>([])
const loading = ref(true)
const totalCount = ref(0)
const nextPage = ref<string | null>(null)
const prevPage = ref<string | null>(null)
const currentPage = ref(1)

async function fetchProducts() {
  loading.value = true
  try {
    const params: Record<string, string> = { page: String(currentPage.value) }
    if (search.value) params.search = search.value
    if (filterActive.value) params.is_active = filterActive.value
    if (filterFeatured.value) params.is_featured = filterFeatured.value

    const res = await apiFetch<any>('/admin/products/', { params })
    products.value = res.results
    totalCount.value = res.count
    nextPage.value = res.next
    prevPage.value = res.previous
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) {
  currentPage.value = page
  fetchProducts()
}

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    fetchProducts()
  }, 350)
}

async function toggleField(product: any, field: string, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  try {
    await apiFetch(`/admin/products/${product.id}/`, { method: 'PATCH', body: { [field]: val } })
    product[field] = val
  } catch {
    ;(e.target as HTMLInputElement).checked = !val
  }
}

onMounted(fetchProducts)
</script>
