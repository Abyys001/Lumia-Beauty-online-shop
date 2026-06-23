<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-[70] lg:hidden"
        @keydown.escape="closeNav"
      >
        <div class="absolute inset-0 bg-lumia-dark/40 backdrop-blur-xs" @click="closeNav" />

        <div
          class="absolute top-0 bottom-0 right-0 w-full max-w-xs sm:max-w-sm bg-base-100 shadow-2xl flex flex-col animate-slide-in-rtl"
          role="dialog"
          aria-label="منوی موبایل"
        >
          <div class="flex items-center justify-between p-4 border-b border-base-200">
            <span class="font-bold text-lg text-lumia-dark">منو</span>
            <button class="btn btn-ghost btn-sm btn-circle" aria-label="بستن منو" @click="closeNav">✕</button>
          </div>

          <nav class="flex-1 overflow-y-auto p-4 space-y-1">
            <NuxtLink to="/" class="nav-link" @click="closeNav">خانه</NuxtLink>
            <NuxtLink to="/shop" class="nav-link" @click="closeNav">فروشگاه</NuxtLink>

            <div class="pt-2">
              <button
                type="button"
                class="nav-link w-full flex items-center justify-between"
                @click="categoriesOpen = !categoriesOpen"
              >
                <span>دسته‌بندی محصولات</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-4 h-4 transition-transform"
                  :class="{ 'rotate-180': categoriesOpen }"
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <div v-if="categoriesOpen" class="mt-1 me-2 border-s-2 border-primary/20 ps-3 space-y-1">
                <div v-for="cat in categories" :key="cat.id">
                  <button
                    type="button"
                    class="w-full flex items-center justify-between py-2 text-sm font-semibold text-base-content hover:text-primary"
                    @click="toggleCategory(cat.id)"
                  >
                    <span>{{ cat.name }}</span>
                    <svg
                      v-if="cat.children?.length"
                      xmlns="http://www.w3.org/2000/svg"
                      class="w-3.5 h-3.5 opacity-40 transition-transform"
                      :class="{ 'rotate-180': openCategories.has(cat.id) }"
                      fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  <div v-if="openCategories.has(cat.id)" class="ps-3 pb-2 space-y-1">
                    <NuxtLink
                      :to="`/shop?category=${cat.slug}`"
                      class="text-xs text-primary font-bold block py-1 hover:underline"
                      @click="closeNav"
                    >
                      مشاهده همه {{ cat.name }}
                    </NuxtLink>
                    <template v-for="sub in cat.children" :key="sub.id">
                      <NuxtLink
                        :to="`/shop?category=${sub.slug}`"
                        class="text-xs font-semibold block py-1 text-base-content/70 hover:text-primary"
                        @click="closeNav"
                      >
                        {{ sub.name }}
                      </NuxtLink>
                      <NuxtLink
                        v-for="item in sub.children || []"
                        :key="item.id"
                        :to="`/shop?category=${item.slug}`"
                        class="text-xs text-base-content/50 block py-0.5 ps-3 hover:text-primary"
                        @click="closeNav"
                      >
                        {{ item.name }}
                      </NuxtLink>
                    </template>
                  </div>
                </div>
              </div>
            </div>

            <NuxtLink to="/blog" class="nav-link" @click="closeNav">وبلاگ</NuxtLink>
            <NuxtLink to="/about" class="nav-link" @click="closeNav">درباره ما</NuxtLink>
            <NuxtLink to="/contact" class="nav-link" @click="closeNav">تماس با ما</NuxtLink>
            <NuxtLink to="/account" class="nav-link" @click="closeNav">حساب کاربری</NuxtLink>
          </nav>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { Category } from '~/types'

const { open, closeNav } = useMobileNav()
const route = useRoute()
const { apiFetch } = useApi()

const categoriesOpen = ref(false)
const openCategories = reactive(new Set<string>())

const { data: categoriesData } = usePublicData(
  'categories',
  () => apiFetch<Category[]>('/categories/'),
  { default: () => [], lazy: true, server: false },
)

const staticCategories: Category[] = [
  { id: 'fragrance', name: 'عطر و ادکلن', slug: 'fragrance', description: '', image: null, mood: '', children: [
    { id: 'womens', name: 'عطر زنانه', slug: 'womens-perfume', description: '', image: null, mood: '', children: [] },
    { id: 'mens', name: 'عطر مردانه', slug: 'mens-perfume', description: '', image: null, mood: '', children: [] },
  ]},
  { id: 'skincare', name: 'مراقبت پوست', slug: 'skincare', description: '', image: null, mood: '', children: [
    { id: 'moisturizers', name: 'مرطوب‌کننده', slug: 'moisturizers', description: '', image: null, mood: '', children: [] },
    { id: 'serums', name: 'سرم', slug: 'serums', description: '', image: null, mood: '', children: [] },
  ]},
]

const categories = computed(() =>
  categoriesData.value?.length ? categoriesData.value : staticCategories,
)

function toggleCategory(id: string) {
  if (openCategories.has(id)) openCategories.delete(id)
  else openCategories.add(id)
}

watch(() => route.path, closeNav)
watch(open, (isOpen) => {
  document.body.style.overflow = isOpen ? 'hidden' : ''
})
</script>

<style scoped>
.nav-link {
  @apply block px-3 py-2.5 rounded-xl text-sm font-medium text-base-content hover:bg-base-200 hover:text-primary transition-colors;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-slide-in-rtl {
  animation: slideInRtl 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideInRtl {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}
</style>
