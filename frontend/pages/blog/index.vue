<template>
  <div class="container-lumia py-8">
    <!-- Header -->
    <div class="text-center max-w-2xl mx-auto mb-12">
      <span class="text-primary font-bold tracking-widest text-xs uppercase block mb-2">مجله زیبایی لومیا</span>
      <h1 class="text-4xl font-extrabold text-base-content mb-3">رازهای سلامت پوست و مو</h1>
      <p class="text-base-content/60 text-sm">راهنماها و مقالات آموزشی تخصصی برای داشتن پوستی شاداب‌تر و رایحه‌ای ماندگارتر</p>
    </div>

    <!-- Featured Post -->
    <div v-if="featuredPost" class="mb-12">
      <NuxtLink
        :to="`/blog/${featuredPost.slug}`"
        class="group grid md:grid-cols-2 gap-6 bg-base-100 rounded-3xl overflow-hidden border border-base-200 shadow-sm transition-all duration-300 hover:shadow-md"
      >
        <div v-if="featuredPost.cover_image" class="aspect-[16/10] md:aspect-auto overflow-hidden relative">
          <img
            v-if="featuredPost.cover_image"
            :src="featuredPost.cover_image"
            :alt="featuredPost.title"
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
        </div>
        
        <div class="p-8 flex flex-col justify-center text-right">
          <span v-if="featuredPost.category" class="inline-block text-xs font-bold text-primary mb-3">
            {{ featuredPost.category.name }}
          </span>
          <h2 class="text-2xl md:text-3xl font-extrabold text-base-content mb-4 group-hover:text-primary transition-colors duration-200 leading-tight">
            {{ featuredPost.title }}
          </h2>
          <p class="text-base-content/75 text-sm leading-relaxed mb-6">
            {{ featuredPost.excerpt }}
          </p>
          
          <div class="flex items-center gap-3 justify-end text-xs text-base-content/40" style="flex-direction: row-reverse;">
            <span>{{ getReadTime(featuredPost.content || '') }} دقیقه مطالعه</span>
            <span class="w-1.5 h-1.5 rounded-full bg-base-content/20"></span>
            <span v-if="featuredPost.published_at">{{ formatDate(featuredPost.published_at) }}</span>
          </div>
        </div>
      </NuxtLink>
    </div>

    <!-- Loading State -->
    <div v-if="pending" class="grid md:grid-cols-3 gap-8">
      <div v-for="i in 3" :key="i" class="space-y-4">
        <div class="skeleton aspect-video w-full rounded-2xl" />
        <div class="skeleton h-4 w-2/3 rounded" />
        <div class="skeleton h-8 w-full rounded" />
      </div>
    </div>

    <!-- Articles Grid -->
    <div v-else>
      <div class="grid md:grid-cols-3 gap-8">
        <NuxtLink
          v-for="post in regularPosts"
          :key="post.id"
          :to="`/blog/${post.slug}`"
          class="group bg-base-100 rounded-3xl overflow-hidden border border-base-200 shadow-xs transition-all duration-300 hover:shadow-md flex flex-col"
        >
          <figure v-if="post.cover_image" class="aspect-[16/10] overflow-hidden">
            <img
              :src="post.cover_image"
              :alt="post.title"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-[1.03]"
              loading="lazy"
            />
          </figure>
          
          <div class="p-6 flex-1 flex flex-col justify-between text-right">
            <div>
              <span v-if="post.category" class="text-xs font-bold text-primary mb-2 block">
                {{ post.category.name }}
              </span>
              <h3 class="font-extrabold text-lg text-base-content mb-3 group-hover:text-primary transition-colors line-clamp-2 leading-snug">
                {{ post.title }}
              </h3>
              <p class="text-sm text-base-content/60 line-clamp-3 leading-relaxed mb-4">
                {{ post.excerpt }}
              </p>
            </div>
            
            <div class="flex items-center justify-end gap-2 text-xs text-base-content/40 border-t border-base-200/50 pt-4" style="flex-direction: row-reverse;">
              <span>{{ getReadTime(post.content || '') }} دقیقه مطالعه</span>
              <span class="w-1.5 h-1.5 rounded-full bg-base-content/20"></span>
              <span v-if="post.published_at">{{ formatDate(post.published_at) }}</span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BlogPost } from '~/types'

const { apiFetch, formatDate } = useApi()

const { data: posts, pending } = await useAsyncData('blog-posts', () =>
  apiFetch<BlogPost[]>('/blog/posts/'),
)

// Extract the first post as the featured post
const featuredPost = computed(() => {
  if (!posts.value || posts.value.length === 0) return null
  return posts.value[0]
})

// The rest of the posts
const regularPosts = computed(() => {
  if (!posts.value || posts.value.length <= 1) return []
  return posts.value.slice(1)
})

function getReadTime(content: string) {
  if (!content) return 3
  const words = content.split(/\s+/).length
  return Math.max(Math.ceil(words / 200), 2)
}

useSeoMeta({
  title: 'مجله زیبایی لومیا | آموزش روتین پوست و آشنایی با عطر نیش',
  description: 'مقالات آموزشی، نکات و راهنماهای تخصصی درباره مراقبت پوست، روتین‌های روزانه، مزایای ترکیباتی مثل PDRN و آبرسان‌ها، و معرفی تخصصی عطرهای نیش.',
  ogTitle: 'مجله زیبایی لومیا بیوتی',
  ogDescription: 'راهنماها و مقالات آموزشی تخصصی برای داشتن پوستی شاداب‌تر با محصولات اورجینال و داشتن رایحه‌ای ماندگارتر',
})

useSchemaOrg([
  defineBreadcrumb({
    itemListElement: [
      { name: 'خانه', item: '/' },
      { name: 'مجله زیبایی', item: '/blog' },
    ],
  }),
])
</script>
