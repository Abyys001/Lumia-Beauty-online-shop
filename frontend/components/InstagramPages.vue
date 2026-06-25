<template>
  <UiSectionShell
    v-if="pending || pages.length"
    title="پیج‌های اینستاگرام لومیا"
    subtitle="هر پیج تخصصی خودش را دارد — از ادکلن و عطر تا مراقبت پوست. ما را دنبال کنید."
    section-class="py-16 md:py-24 bg-lumia-cream/20 border-t border-lumia-cream content-auto"
  >
    <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
      <div v-for="i in 3" :key="i" class="skeleton h-36 sm:h-40 rounded-3xl" />
    </div>

    <div
      v-else
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 max-w-5xl mx-auto"
    >
      <a
        v-for="page in pages"
        :key="page.id"
        :href="page.profile_url"
        target="_blank"
        rel="noopener noreferrer"
        class="group relative flex items-center gap-4 sm:gap-5 p-5 sm:p-6 rounded-3xl bg-white border border-lumia-cream/80 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-500 ease-out overflow-hidden"
      >
        <div
          class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
          aria-hidden="true"
          style="background: linear-gradient(135deg, rgba(131,58,180,0.06) 0%, rgba(253,29,29,0.05) 50%, rgba(252,176,69,0.06) 100%)"
        />

        <div
          class="relative flex-shrink-0 w-14 h-14 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center text-white shadow-md group-hover:scale-105 transition-transform duration-500"
          style="background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 sm:w-8 sm:h-8" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
          </svg>
        </div>

        <div class="relative flex-1 min-w-0 text-right">
          <p class="text-xs sm:text-sm text-lumia-dark/55 mb-1 leading-relaxed">
            {{ page.label }}
          </p>
          <p class="font-bold text-lumia-dark text-base sm:text-lg truncate" dir="ltr">
            @{{ displayUsername(page.username) }}
          </p>
        </div>

        <div class="relative flex-shrink-0 w-9 h-9 rounded-full border border-lumia-gold/30 flex items-center justify-center text-lumia-gold group-hover:bg-lumia-gold group-hover:text-lumia-dark group-hover:border-lumia-gold transition-all duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </a>
    </div>
  </UiSectionShell>
</template>

<script setup lang="ts">
import type { InstagramPage } from '~/types'

const { apiFetch } = useApi()

const { data: pagesData, pending } = await usePublicData(
  'instagram-pages',
  () => apiFetch<InstagramPage[]>('/cms/instagram-pages/'),
  { default: () => [] },
)

const pages = computed(() => pagesData.value || [])

function displayUsername(username: string) {
  return (username || '').replace(/^@/, '')
}
</script>
