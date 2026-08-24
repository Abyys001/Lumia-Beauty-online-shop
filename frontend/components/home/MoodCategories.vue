<template>
  <UiSectionShell
    title="دسته‌بندی‌های حسی"
    subtitle="محصولات را بر اساس حس و حال، نت‌های رایحه یا نوع کاربرد آرایشی و بهداشتی انتخاب کنید."
    section-class="py-12 md:py-20"
  >
    <div class="flex flex-col gap-5 md:gap-8">
      <div
        v-for="block in blocks"
        :key="block.id"
        class="rounded-3xl bg-white border border-lumia-cream shadow-sm overflow-hidden"
      >
        <div class="flex items-center justify-between gap-3 p-4 sm:p-6 border-b border-lumia-cream/80">
          <h3 class="text-lg sm:text-xl font-bold text-lumia-dark flex items-center gap-2">
            <span class="text-2xl">{{ block.emoji }}</span>
            <span>{{ block.title }}</span>
          </h3>
          <NuxtLink
            :to="block.shopLink"
            class="text-xs sm:text-sm font-semibold text-lumia-gold hover:underline shrink-0"
          >
            مشاهده همه
          </NuxtLink>
        </div>

        <div v-if="block.categories.length" class="px-4 sm:px-6 pt-4 sm:pt-6 overflow-hidden min-w-0">
          <div class="category-scroll">
            <NuxtLink
              v-for="cat in block.categories"
              :key="cat.id"
              :to="`/shop?category=${cat.slug}`"
              class="category-card group"
            >
              <div class="category-avatar">
                <AppImage
                  v-if="cat.image"
                  :src="cat.image"
                  :alt="cat.name"
                  img-class="w-full h-full object-cover"
                />
                <span v-else class="text-2xl sm:text-3xl">{{ moodEmoji(cat) }}</span>
              </div>
              <span class="category-label">{{ cat.name }}</span>
            </NuxtLink>
          </div>
        </div>

        <div class="p-4 sm:p-6">
          <div v-if="pending && !block.products.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <div v-for="n in 4" :key="n" class="aspect-[3/4] rounded-2xl bg-lumia-cream/40 animate-pulse" />
          </div>
          <div v-else-if="block.products.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <ProductCard
              v-for="product in block.products"
              :key="product.id"
              :product="product"
              show-quick-add
            />
          </div>
          <p v-else class="text-sm text-base-content/50 text-center py-8">
            به‌زودی محصولات این بخش اضافه می‌شود.
          </p>
        </div>
      </div>
    </div>
  </UiSectionShell>
</template>

<script setup lang="ts">
import type { Category, PaginatedResponse, Product } from '~/types'

const props = defineProps<{
  categories: Category[]
}>()

const { apiFetch } = useApi()

const PRODUCTS_PER_BLOCK = 4

/** Keyword buckets — the live catalogue is a flat list of categories with no parents. */
const FRAGRANCE_KEYWORDS = ['عطر', 'ادکلن', 'اسپری', 'دئودورانت', 'خوشبو', 'fragrance', 'perfume', 'deodorant']
const HYGIENE_KEYWORDS = [
  'بهداشت', 'شوینده', 'مراقب', 'پوست', 'مو', 'آرایش', 'دهان', 'دندان',
  'hygiene', 'care', 'skincare', 'haircare', 'makeup',
]

const moodEmojis: Record<string, string> = {
  cool: '❄️',
  sweet: '🍯',
  warm: '🔥',
  bitter: '🌿',
  haircare: '💇',
  skincare: '✨',
  hygiene: '🧼',
  خنک: '❄️',
  شیرین: '🍯',
  گرم: '🔥',
  تلخ: '🌿',
}

function matches(cat: Category, keywords: string[]) {
  const haystack = `${cat.name} ${cat.slug} ${cat.mood || ''}`.toLowerCase()
  return keywords.some(k => haystack.includes(k.toLowerCase()))
}

/** A category and, when it is a parent, its children — all of them can hold products. */
function withChildren(cats: Category[]): Category[] {
  return cats.flatMap(cat => [cat, ...(cat.children || [])])
}

const fragranceCategories = computed(() =>
  withChildren(props.categories.filter(c => matches(c, FRAGRANCE_KEYWORDS))),
)

const hygieneCategories = computed(() => {
  const taken = new Set(fragranceCategories.value.map(c => c.slug))
  return withChildren(
    props.categories.filter(c => !taken.has(c.slug) && matches(c, HYGIENE_KEYWORDS)),
  )
})

async function fetchProducts(slugs: string[]): Promise<Product[]> {
  const query: Record<string, string | number> = {
    ordering: '-sales_count',
    page_size: PRODUCTS_PER_BLOCK,
  }
  if (slugs.length) query.categories = slugs.join(',')

  const page = await apiFetch<PaginatedResponse<Product>>('/products/', { query }).catch(() => null)
  return page?.results || []
}

/** Never leave a block empty — fall back to the best sellers when a bucket has no stock. */
async function fetchWithFallback(slugs: string[]): Promise<Product[]> {
  const scoped = await fetchProducts(slugs)
  return scoped.length ? scoped : await fetchProducts([])
}

const { data: blockProducts, pending } = await useAsyncData(
  'mood-block-products',
  async () => {
    const [fragrance, hygiene] = await Promise.all([
      fetchWithFallback(fragranceCategories.value.map(c => c.slug)),
      fetchWithFallback(hygieneCategories.value.map(c => c.slug)),
    ])
    return { fragrance, hygiene }
  },
  {
    default: () => ({ fragrance: [] as Product[], hygiene: [] as Product[] }),
    watch: [fragranceCategories, hygieneCategories],
  },
)

function shopLink(cats: Category[]) {
  return cats.length ? `/shop?category=${cats[0].slug}` : '/shop'
}

const blocks = computed(() => [
  {
    id: 'fragrance',
    emoji: '✨',
    title: 'دنیای خوش‌بوکننده‌ها',
    categories: fragranceCategories.value,
    products: blockProducts.value?.fragrance || [],
    shopLink: shopLink(fragranceCategories.value),
  },
  {
    id: 'hygiene',
    emoji: '🧴',
    title: 'محصولات بهداشتی و مراقبتی',
    categories: hygieneCategories.value,
    products: blockProducts.value?.hygiene || [],
    shopLink: shopLink(hygieneCategories.value),
  },
])

function moodEmoji(cat: Category) {
  const key = (cat.mood || cat.slug).toLowerCase()
  for (const [k, emoji] of Object.entries(moodEmojis)) {
    if (key.includes(k) || cat.name.includes(k)) return emoji
  }
  return '🌸'
}
</script>

<style scoped>
.category-scroll {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  min-width: 0;
  padding-bottom: 0.25rem;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.category-scroll::-webkit-scrollbar {
  display: none;
}

.category-card {
  @apply flex flex-col items-center text-center shrink-0 snap-start;
  @apply p-3 sm:p-4 rounded-2xl bg-lumia-cream/20 hover:bg-lumia-cream/50 transition-all duration-300 border border-transparent hover:border-lumia-gold/20;
  width: 7rem;
}

.category-avatar {
  @apply w-14 h-14 sm:w-16 sm:h-16 rounded-full overflow-hidden bg-white shadow-sm flex items-center justify-center group-hover:scale-105 transition-transform duration-300;
}

.category-label {
  @apply font-semibold text-xs sm:text-sm mt-2.5 text-lumia-dark leading-snug line-clamp-2;
}
</style>
