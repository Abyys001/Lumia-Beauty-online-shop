<template>
  <UiSectionShell
    title="دسته‌بندی‌های حسی"
    subtitle="محصولات را بر اساس حس و حال، نت‌های رایحه یا نوع کاربرد آرایشی و بهداشتی انتخاب کنید."
    section-class="py-12 md:py-20"
  >
    <div class="flex flex-col gap-5 md:gap-8">
      <!-- Fragrance block -->
      <div class="rounded-3xl bg-white border border-lumia-cream shadow-sm overflow-hidden">
        <div class="flex items-center justify-between gap-3 p-4 sm:p-6 border-b border-lumia-cream/80">
          <h3 class="text-lg sm:text-xl font-bold text-lumia-dark flex items-center gap-2">
            <span class="text-2xl">✨</span>
            <span>{{ fragranceParent?.name || 'دنیای خوش‌بوکننده‌ها' }}</span>
          </h3>
          <NuxtLink
            v-if="fragranceParent"
            :to="`/shop?category=${fragranceParent.slug}`"
            class="text-xs sm:text-sm font-semibold text-lumia-gold hover:underline shrink-0"
          >
            مشاهده همه
          </NuxtLink>
        </div>

        <div v-if="fragranceItems.length" class="p-4 sm:p-6">
          <div class="category-scroll fragrance-grid">
            <NuxtLink
              v-for="cat in fragranceItems"
              :key="cat.id"
              :to="categoryLink(cat)"
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
        <p v-else class="text-sm text-base-content/50 text-center py-8 px-4">به‌زودی دسته‌بندی‌های جدید اضافه می‌شود.</p>
      </div>

      <!-- Hygiene block -->
      <div class="rounded-3xl bg-white border border-lumia-cream shadow-sm overflow-hidden">
        <div class="flex items-center justify-between gap-3 p-4 sm:p-6 border-b border-lumia-cream/80">
          <h3 class="text-lg sm:text-xl font-bold text-lumia-dark flex items-center gap-2">
            <span class="text-2xl">🧴</span>
            <span>{{ hygieneParent?.name || 'محصولات بهداشتی' }}</span>
          </h3>
          <NuxtLink
            v-if="hygieneParent"
            :to="`/shop?category=${hygieneParent.slug}`"
            class="text-xs sm:text-sm font-semibold text-lumia-gold hover:underline shrink-0"
          >
            مشاهده همه
          </NuxtLink>
        </div>

        <div v-if="hygieneItems.length" class="p-4 sm:p-6">
          <div class="category-scroll hygiene-grid">
            <NuxtLink
              v-for="cat in hygieneItems"
              :key="cat.id"
              :to="categoryLink(cat)"
              class="category-card group"
            >
              <div class="category-avatar category-avatar-sm">
                <AppImage
                  v-if="cat.image"
                  :src="cat.image"
                  :alt="cat.name"
                  img-class="w-full h-full object-cover"
                />
                <span v-else class="text-xl sm:text-2xl">{{ moodEmoji(cat) }}</span>
              </div>
              <span class="category-label category-label-sm">{{ cat.name }}</span>
            </NuxtLink>
          </div>
        </div>
        <p v-else class="text-sm text-base-content/50 text-center py-8 px-4">به‌زودی دسته‌بندی‌های جدید اضافه می‌شود.</p>
      </div>
    </div>
  </UiSectionShell>
</template>

<script setup lang="ts">
import type { Category } from '~/types'

const props = defineProps<{
  categories: Category[]
}>()

const FRAGRANCE_SLUGS = ['fragrances', 'fragrance', 'perfume', 'perfumes']
const HYGIENE_SLUGS = ['hygiene', 'personal-care', 'skincare', 'haircare']

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

function findParent(slugs: string[], nameHint: string) {
  return props.categories.find(c =>
    slugs.includes(c.slug)
    || c.name.includes(nameHint),
  ) ?? null
}

const fragranceParent = computed(() => findParent(FRAGRANCE_SLUGS, 'خوشبو'))
const hygieneParent = computed(() => findParent(HYGIENE_SLUGS, 'بهداشتی'))

function sortedChildren(parent: Category | null) {
  if (!parent?.children?.length) return []
  return [...parent.children]
}

const fragranceItems = computed(() => sortedChildren(fragranceParent.value))

const hygieneItems = computed(() => sortedChildren(hygieneParent.value))

function categoryLink(cat: Category) {
  return `/shop?category=${cat.slug}`
}

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
  padding-bottom: 0.25rem;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.category-scroll::-webkit-scrollbar {
  display: none;
}

@media (min-width: 768px) {
  .category-scroll {
    display: grid;
    overflow: visible;
    padding-bottom: 0;
    scroll-snap-type: none;
  }
  .fragrance-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
  .hygiene-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
  }
}

@media (min-width: 1024px) {
  .fragrance-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.category-card {
  @apply flex flex-col items-center text-center shrink-0 snap-start;
  width: 7.5rem;
}
@media (min-width: 640px) {
  .category-card {
    width: auto;
  }
}

.category-card {
  @apply p-3 sm:p-4 rounded-2xl bg-lumia-cream/20 hover:bg-lumia-cream/50 transition-all duration-300 border border-transparent hover:border-lumia-gold/20;
}

.category-avatar {
  @apply w-14 h-14 sm:w-16 sm:h-16 rounded-full overflow-hidden bg-white shadow-sm flex items-center justify-center group-hover:scale-105 transition-transform duration-300;
}
.category-avatar-sm {
  @apply w-12 h-12 sm:w-14 sm:h-14;
}

.category-label {
  @apply font-semibold text-xs sm:text-sm mt-2.5 text-lumia-dark leading-snug line-clamp-2;
}
.category-label-sm {
  @apply text-[11px] sm:text-xs;
}
</style>
