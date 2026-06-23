<template>
  <UiSectionShell
    title="ویترین اینستاگرام لومیا"
    subtitle="ما را در اینستاگرام دنبال کنید تا از آخرین روتین‌های روزانه، معرفی عطرها و رضایت مشتریان باخبر شوید."
    section-class="py-16 md:py-24 bg-lumia-cream/20 border-t border-lumia-cream content-auto"
  >
    <div class="text-center mb-8">
      <a
        href="https://instagram.com/lumia.beauty"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center gap-2 px-6 py-2 rounded-full border border-lumia-gold text-lumia-gold hover:bg-lumia-gold hover:text-lumia-dark transition-all duration-300 font-semibold text-sm"
      >
        <span>@lumia.beauty</span>
      </a>
    </div>

    <div v-if="pending" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="skeleton aspect-square rounded-3xl" />
    </div>

    <div v-else-if="!posts.length" class="text-center py-12 text-base-content/50">
      <p>به‌زودی پست‌های اینستاگرام اینجا نمایش داده می‌شود.</p>
    </div>

    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <a
        v-for="(post, index) in posts"
        :key="post.id"
        :href="post.post_url"
        target="_blank"
        rel="noopener noreferrer"
        class="group relative aspect-square rounded-3xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-500 bg-white"
      >
        <img
          v-if="post.image"
          :src="normalizeMediaUrl(post.image) || post.image"
          :alt="post.caption || 'Lumia Beauty Instagram'"
          class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
          loading="lazy"
        />

        <div class="absolute inset-0 bg-lumia-dark/60 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-between p-3 sm:p-6 text-white">
          <p class="text-sm font-medium leading-relaxed line-clamp-3 text-right">
            {{ post.caption || 'مشاهده در پیج ما' }}
          </p>
          <div class="flex items-center gap-4 text-xs font-semibold text-white/95">
            <span>❤️ {{ getMockLikes(index) }}</span>
            <span>💬 {{ getMockComments(index) }}</span>
          </div>
        </div>
      </a>
    </div>
  </UiSectionShell>
</template>

<script setup lang="ts">
import type { InstagramPost, PaginatedResponse } from '~/types'

const { apiFetch } = useApi()
const { normalizeMediaUrl } = useMediaUrl()

const { data: postsData, pending } = await usePublicData(
  'instagram',
  () => apiFetch<PaginatedResponse<InstagramPost>>('/instagram/'),
  { default: () => ({ count: 0, next: null, previous: null, results: [] }) },
)

const posts = computed(() => postsData.value?.results || [])

function getMockLikes(index: number) {
  const likes = [1248, 854, 1892, 946]
  return likes[index % likes.length] + ' پسند'
}

function getMockComments(index: number) {
  const comments = [84, 52, 142, 38]
  return comments[index % comments.length] + ' نظر'
}
</script>
