<template>
  <section class="relative min-h-[75vh] md:min-h-[85vh] flex items-center overflow-hidden py-12 md:py-20 bg-lumia-cream/30">
    <div class="absolute inset-0 z-0 overflow-hidden">
      <img
        :src="posterUrl"
        :alt="hero?.headline || 'Lumia Beauty'"
        class="w-full h-full object-cover object-center"
        fetchpriority="high"
        loading="eager"
        decoding="async"
      />
      <video
        v-if="showVideo"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        :poster="posterUrl"
        class="absolute inset-0 w-full h-full object-cover object-center"
      >
        <source :src="videoUrl!" type="video/webm" />
      </video>
      <div class="absolute inset-0 bg-gradient-to-r from-lumia-dark/80 via-lumia-dark/50 to-transparent rtl:bg-gradient-to-l" />
    </div>

    <div class="container-lumia relative z-10 w-full">
      <div class="max-w-2xl text-white space-y-4 sm:space-y-6 md:space-y-8 p-4 sm:p-6 md:p-8 rounded-3xl bg-lumia-dark/30 backdrop-blur-md border border-white/10 shadow-2xl">
        <span
          v-if="hero?.badge_text"
          class="inline-block px-4 py-1.5 rounded-full bg-lumia-gold text-lumia-dark font-semibold text-xs tracking-wider uppercase"
        >
          {{ hero.badge_text }}
        </span>
        <h1 class="text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold leading-tight md:leading-normal">
          {{ hero?.headline || 'رایحه‌ای که امضای توست؛' }}
          <span class="block text-lumia-gold mt-2">{{ hero?.subheadline || 'روتینی که پوستت لایق آن است' }}</span>
        </h1>
        <p class="text-sm md:text-lg text-white/80 leading-relaxed max-w-xl font-light">
          {{ hero?.description || 'در لومیا بیوتی، اصالت محصول، پاکیزگی بسته‌بندی و مشاوره تخصصی در هم آمیخته‌اند.' }}
        </p>
        <div class="flex flex-wrap gap-4 pt-2">
          <NuxtLink
            :to="hero?.cta_url || '/shop'"
            class="px-8 py-3.5 rounded-full bg-lumia-gold hover:bg-white text-lumia-dark font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center gap-2"
          >
            {{ hero?.cta_text || 'کشف رایحه تو' }}
          </NuxtLink>
          <NuxtLink
            :to="hero?.cta_secondary_url || '/blog'"
            class="px-8 py-3.5 rounded-full bg-transparent hover:bg-white/10 text-white border border-white/30 font-medium transition-all duration-300"
          >
            {{ hero?.cta_secondary_text || 'مجله زیبایی لومیا' }}
          </NuxtLink>
          <ClientOnly>
            <NuxtLink
              v-if="auth.user?.is_staff"
              to="/admin"
              class="px-8 py-3.5 rounded-full bg-white/10 hover:bg-white/20 text-white border border-lumia-gold/50 font-semibold transition-all duration-300 flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              ورود به پنل مدیریت
            </NuxtLink>
          </ClientOnly>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { HomeHero } from '~/types'

const DEFAULT_POSTER = '/images/hero_banner.png'

const props = defineProps<{
  hero: HomeHero | null
}>()

const auth = useAuthStore()
const { normalizeMediaUrl } = useMediaUrl()
const isMounted = ref(false)

onMounted(() => {
  isMounted.value = true
})

function resolveMediaUrl(value: string | null | undefined): string | null {
  return normalizeMediaUrl(value)
}

const posterUrl = computed(() =>
  resolveMediaUrl(props.hero?.video_poster_url)
    || resolveMediaUrl(props.hero?.fallback_image_url)
    || DEFAULT_POSTER,
)

const videoUrl = computed(() => resolveMediaUrl(props.hero?.video_webm_url))

const showVideo = computed(() => isMounted.value && Boolean(videoUrl.value))
</script>
