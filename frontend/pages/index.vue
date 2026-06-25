<template>
  <div class="bg-lumia-light/50">
    <HomeHeroSection :hero="cms?.hero || null" />
    <HomeTrustBadges :badges="cms?.trust_badges || []" />
    <HomeMoodCategories :categories="categories || []" />
    <HomeProductCarousel :products="featuredProducts" :pending="pending" />
    <InstagramPages />
  </div>
</template>

<script setup lang="ts">
import type { Category, HomeCMS, PaginatedResponse, Product } from '~/types'

const { apiFetch } = useApi()
const config = useRuntimeConfig()

useSeoMeta({
  title: 'لومیا بیوتی | فروشگاه آنلاین آرایشی، بهداشتی و خوش‌بوکننده لوکس',
  description: 'خرید اینترنتی انواع عطر و ادکلن‌های اصل، محصولات مراقبت پوست و مو با ارسال مطمئن به سراسر ایران در لومیا بیوتی.',
  ogTitle: 'لومیا بیوتی — رایحه‌ای که امضای توست',
  ogDescription: 'رایحه‌ای که امضای توست؛ روتینی که پوستت لایق آن است.',
  ogUrl: config.public.siteUrl,
  ogImage: `${config.public.siteUrl}/images/hero_banner.png`,
  twitterCard: 'summary_large_image',
})

useSchemaOrg([
  defineWebSite({ name: 'لومیا بیوتی', url: config.public.siteUrl }),
  defineOrganization({ name: 'Lumia Beauty', url: config.public.siteUrl }),
])

type HomeData = {
  cms: HomeCMS
  categories: Category[]
  featured: Product[]
}

const emptyHome: HomeData = {
  cms: { hero: null, trust_badges: [] },
  categories: [],
  featured: [],
}

const { data: homeData, pending } = await usePublicData<HomeData>(
  'home',
  async () => {
    const [cms, categories, featured] = await Promise.all([
      apiFetch<HomeCMS>('/cms/home/').catch(() => emptyHome.cms),
      apiFetch<Category[]>('/categories/').catch(() => [] as Category[]),
      apiFetch<Product[]>('/products/featured/').catch(() => [] as Product[]),
    ])

    let products = featured
    if (!products.length) {
      const fallback = await apiFetch<PaginatedResponse<Product>>('/products/', {
        query: { ordering: '-sales_count', page_size: 8 },
      }).catch(() => null)
      products = fallback?.results || []
    }

    return { cms, categories, featured: products }
  },
  { default: () => emptyHome },
)

const cms = computed(() => homeData.value?.cms || emptyHome.cms)
const categories = computed(() => homeData.value?.categories || [])
const featuredProducts = computed(() => homeData.value?.featured || [])

const { normalizeMediaUrl } = useMediaUrl()

const posterUrl = computed(() =>
  normalizeMediaUrl(cms.value?.hero?.video_poster_url)
    || normalizeMediaUrl(cms.value?.hero?.fallback_image_url)
    || '/images/hero_banner.png',
)

useHead({
  link: [
    { rel: 'preload', as: 'image', href: posterUrl.value, fetchPriority: 'high' },
  ],
})
</script>
