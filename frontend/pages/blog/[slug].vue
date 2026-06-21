<template>
  <article v-if="post" class="container-lumia py-8 max-w-4xl mx-auto">
    <!-- Breadcrumbs -->
    <div class="flex gap-2 text-xs text-base-content/40 mb-6 justify-end" style="flex-direction: row-reverse;">
      <NuxtLink to="/" class="hover:text-primary">خانه</NuxtLink>
      <span>/</span>
      <NuxtLink to="/blog" class="hover:text-primary">مجله زیبایی</NuxtLink>
      <span>/</span>
      <span class="text-base-content/60 truncate max-w-[150px]">{{ post.title }}</span>
    </div>

    <!-- Editorial Header -->
    <header class="text-center mb-8 max-w-2xl mx-auto">
      <span v-if="post.category" class="inline-block text-xs font-extrabold text-primary mb-3 uppercase tracking-wider">
        {{ post.category.name }}
      </span>
      <h1 class="text-3xl md:text-4xl font-extrabold text-base-content mb-4 leading-tight">
        {{ post.title }}
      </h1>
      
      <!-- Meta details -->
      <div class="flex items-center justify-center gap-3 text-xs text-base-content/50" style="flex-direction: row-reverse;">
        <span>نویسنده: {{ post.author_name || 'لومیا بیوتی' }}</span>
        <span class="w-1.5 h-1.5 rounded-full bg-base-content/20"></span>
        <span>{{ readTime }} دقیقه مطالعه</span>
        <span class="w-1.5 h-1.5 rounded-full bg-base-content/20"></span>
        <span v-if="post.published_at">{{ formatDate(post.published_at) }}</span>
      </div>
    </header>

    <!-- Cover Image -->
    <figure v-if="post.cover_image" class="rounded-3xl overflow-hidden mb-10 shadow-sm aspect-[21/9]">
      <img
        v-if="post.cover_image"
        :src="post.cover_image"
        :alt="post.title"
        class="w-full h-[300px] md:h-[500px] object-cover rounded-3xl shadow-sm"
      />
    </figure>

    <!-- Article Content -->
    <div class="prose max-w-none text-base-content/85 leading-relaxed text-right dir-rtl whitespace-pre-line text-lg font-serif mb-16 px-2">
      {{ post.content }}
    </div>

    <!-- Tags -->
    <div v-if="post.tags?.length" class="flex flex-wrap gap-2 justify-end mb-16 border-b border-base-200 pb-8" style="flex-direction: row-reverse;">
      <span class="text-sm text-base-content/50 ml-2 pt-1">برچسب‌ها:</span>
      <span
        v-for="tag in post.tags"
        :key="tag.slug"
        class="text-xs bg-base-200 text-base-content/70 px-3 py-1.5 rounded-full hover:bg-primary/10 hover:text-primary transition-colors"
      >
        #{{ tag.name }}
      </span>
    </div>

    <!-- Related Products Conversion Block -->
    <div v-if="productsData?.results?.length" class="border-t border-base-200 pt-12">
      <h3 class="text-2xl font-bold mb-8 text-right">محصولات پیشنهادی این مقاله</h3>
      
      <div class="grid grid-cols-2 md:grid-cols-3 gap-6">
        <NuxtLink
          v-for="product in productsData.results.slice(0, 3)"
          :key="product.id"
          :to="`/shop/${product.slug}`"
          class="group bg-base-100 rounded-2xl overflow-hidden border border-base-200 shadow-xs transition-all duration-300 hover:shadow-md text-right flex flex-col"
        >
          <div class="aspect-square overflow-hidden bg-base-200 relative">
            <img
              v-if="product.primary_image"
              :src="product.primary_image"
              :alt="product.name"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              loading="lazy"
            />
            <span v-if="product.discount_percent" class="absolute top-2 right-2 badge badge-error font-bold">
              {{ product.discount_percent }}٪ تخفیف
            </span>
          </div>
          
          <div class="p-4 flex-1 flex flex-col justify-between">
            <div>
              <p class="text-xs text-base-content/50 mb-1">{{ product.brand_name }}</p>
              <h4 class="font-bold text-sm text-base-content group-hover:text-primary transition-colors line-clamp-2 leading-snug mb-2">
                {{ product.name }}
              </h4>
            </div>
            
            <div class="flex items-center gap-1.5 mt-2 justify-start" style="flex-direction: row-reverse;">
              <span class="font-bold text-sm text-primary">{{ formatPrice(product.price) }} تومان</span>
              <span v-if="product.compare_at_price" class="text-xs text-base-content/30 line-through">
                {{ formatPrice(product.compare_at_price) }}
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { BlogPost, Product } from '~/types'

const route = useRoute()
const { apiFetch, formatDate, formatPrice } = useApi()

// Fetch Post Details
const { data: post } = await useAsyncData(
  `blog-${route.params.slug}`,
  () => apiFetch<BlogPost>(`/blog/posts/${route.params.slug}/`),
)

// Fetch Suggested Products
const { data: productsData } = await useAsyncData(
  'blog-related-products',
  () => apiFetch<{ results: Product[] }>('/products/?is_featured=true&limit=3')
)

// Read time estimation
const readTime = computed(() => {
  if (!post.value?.content) return 3
  const words = post.value.content.split(/\s+/).length
  return Math.max(Math.ceil(words / 200), 2)
})

if (post.value) {
  useSeoMeta({
    title: post.value.meta_title || `${post.value.title} | مجله زیبایی لومیا`,
    description: post.value.meta_description || post.value.excerpt,
    ogTitle: post.value.title,
    ogDescription: post.value.excerpt,
    ogImage: post.value.cover_image || undefined,
  })

  useSchemaOrg([
    defineArticle({
      headline: post.value.title,
      description: post.value.excerpt,
      image: post.value.cover_image,
      datePublished: post.value.published_at,
      author: {
        name: post.value.author_name || 'مدیریت لومیا بیوتی',
      },
      publisher: {
        name: 'لومیا بیوتی',
        logo: '/images/hero_banner.png',
      },
    }),
    defineBreadcrumb({
      itemListElement: [
        { name: 'خانه', item: '/' },
        { name: 'مجله زیبایی', item: '/blog' },
        { name: post.value.title, item: route.path },
      ],
    }),
  ])
}
</script>

<style scoped>
/* Elegant typography for luxury magazine */
.font-serif {
  font-family: 'Outfit', 'Georgia', 'Times New Roman', serif;
}
</style>
