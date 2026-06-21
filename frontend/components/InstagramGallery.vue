<template>
  <section class="py-16 md:py-24 bg-lumia-cream/20 border-t border-lumia-cream">
    <div class="container-lumia">
      <div class="text-center max-w-xl mx-auto mb-12">
        <h2 class="section-title text-3xl font-bold">ویترین اینستاگرام لومیا</h2>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-3"></div>
        <p class="section-subtitle text-sm text-base-content/70">
          ما را در اینستاگرام دنبال کنید تا از آخرین روتین‌های روزانه، معرفی عطرها و رضایت مشتریان باخبر شوید.
        </p>
        <a
          href="https://instagram.com/lumia.beauty"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 mt-4 px-6 py-2 rounded-full border border-lumia-gold text-lumia-gold hover:bg-lumia-gold hover:text-lumia-dark transition-all duration-300 font-semibold text-sm"
        >
          <span>@lumia.beauty</span>
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
          </svg>
        </a>
      </div>

      <div v-if="pending" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="skeleton aspect-square rounded-3xl" />
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <a
          v-for="(post, index) in postsData?.results || []"
          :key="post.id"
          :href="post.post_url"
          target="_blank"
          rel="noopener noreferrer"
          class="group relative aspect-square rounded-3xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-500 bg-white"
        >
          <img
            v-if="post.image"
            :src="post.image"
            :alt="post.caption || 'Lumia Beauty Instagram'"
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            loading="lazy"
          />
          
          <!-- Realistic IG Hover Overlay -->
          <div class="absolute inset-0 bg-lumia-dark/60 opacity-0 group-hover:opacity-100 transition-all duration-300 flex flex-col justify-between p-6 text-white">
            <!-- Header Icon -->
            <div class="flex justify-end">
              <svg class="w-6 h-6 fill-current text-lumia-gold" viewBox="0 0 24 24">
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
              </svg>
            </div>

            <!-- Description -->
            <p class="text-sm font-medium leading-relaxed line-clamp-3 text-right">
              {{ post.caption || 'مشاهده در پیج ما' }}
            </p>

            <!-- Stats simulator -->
            <div class="flex items-center gap-4 text-xs font-semibold text-white/95">
              <span class="flex items-center gap-1">
                <span>❤️</span> <span>{{ getMockLikes(index) }}</span>
              </span>
              <span class="flex items-center gap-1">
                <span>💬</span> <span>{{ getMockComments(index) }}</span>
              </span>
            </div>
          </div>
        </a>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { InstagramPost, PaginatedResponse } from '~/types'

const { apiFetch } = useApi()

const { data: postsData, pending } = await useAsyncData('instagram', () =>
  apiFetch<PaginatedResponse<InstagramPost>>('/instagram/'),
)

function getMockLikes(index: number) {
  const likes = [1248, 854, 1892, 946]
  return likes[index % likes.length] + ' پسند'
}

function getMockComments(index: number) {
  const comments = [84, 52, 142, 38]
  return comments[index % comments.length] + ' نظر'
}
</script>
