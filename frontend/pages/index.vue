<template>
  <div class="bg-lumia-light/50">
    <!-- Hero Section -->
    <section class="relative min-h-[75vh] md:min-h-[85vh] flex items-center overflow-hidden py-12 md:py-20 bg-lumia-cream/30">
      <!-- Background Image with Overlay -->
      <div class="absolute inset-0 z-0">
        <NuxtImg
          src="/images/hero_banner.png"
          alt="Lumia Beauty Banner"
          class="w-full h-full object-cover object-center transform scale-105"
          format="webp"
          quality="90"
        />
        <div class="absolute inset-0 bg-gradient-to-r from-lumia-dark/80 via-lumia-dark/50 to-transparent rtl:bg-gradient-to-l"></div>
      </div>

      <!-- Hero Content -->
      <div class="container-lumia relative z-10 w-full">
        <div class="max-w-2xl text-white space-y-6 md:space-y-8 p-6 md:p-8 rounded-3xl bg-lumia-dark/30 backdrop-blur-md border border-white/10 shadow-2xl animate-fade-in-up">
          <span class="inline-block px-4 py-1.5 rounded-full bg-lumia-gold text-lumia-dark font-semibold text-xs tracking-wider uppercase">
            شکوه اصالت و زیبایی
          </span>
          <h1 class="text-3xl md:text-5xl lg:text-6xl font-bold leading-tight md:leading-normal">
            رایحه‌ای که امضای توست؛
            <span class="block text-lumia-gold mt-2">روتینی که پوستت لایق آن است</span>
          </h1>
          <p class="text-sm md:text-lg text-white/80 leading-relaxed max-w-xl font-light">
            در لومیا بیوتی، اصالت محصول، پاکیزگی بسته‌بندی و مشاوره تخصصی در هم آمیخته‌اند تا بهترین حس و رایحه را به زندگی روزمره‌تان تزریق کنند.
          </p>
          <div class="flex flex-wrap gap-4 pt-2">
            <NuxtLink to="/shop" class="px-8 py-3.5 rounded-full bg-lumia-gold hover:bg-white text-lumia-dark font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center gap-2">
              <span>کشف رایحه تو</span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </NuxtLink>
            <NuxtLink to="/blog" class="px-8 py-3.5 rounded-full bg-transparent hover:bg-white/10 text-white border border-white/30 font-medium transition-all duration-300">
              مجله زیبایی لومیا
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust Badges -->
    <section class="py-8 bg-lumia-dark text-white border-y border-lumia-gold/20">
      <div class="container-lumia">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div v-for="badge in trustBadges" :key="badge.title" class="group flex flex-col items-center p-4 transition-all duration-300 hover:-translate-y-1">
            <div class="w-12 h-12 rounded-full bg-lumia-gold/10 border border-lumia-gold/30 flex items-center justify-center mb-3 group-hover:bg-lumia-gold group-hover:text-lumia-dark transition-all duration-300">
              <span class="text-xl" v-html="badge.icon"></span>
            </div>
            <h4 class="font-semibold text-sm md:text-base text-lumia-gold">{{ badge.title }}</h4>
            <p class="text-xs text-white/60 mt-1">{{ badge.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Visual Mood Categories -->
    <section class="py-16 md:py-24 container-lumia">
      <div class="text-center max-w-xl mx-auto mb-12 md:mb-16">
        <h2 class="section-title text-3xl font-bold">دسته‌بندی‌های حسی</h2>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-3"></div>
        <p class="section-subtitle text-sm text-base-content/70">
          محصولات را بر اساس حس و حال، نت‌های رایحه یا نوع کاربرد آرایشی و بهداشتی انتخاب کنید.
        </p>
      </div>

      <!-- Categories Layout -->
      <div class="grid md:grid-cols-2 gap-12">
        <!-- Fragrance moods -->
        <div class="p-8 rounded-3xl bg-white border border-lumia-cream shadow-sm hover:shadow-md transition-shadow">
          <h3 class="text-xl font-bold mb-6 text-lumia-dark pb-3 border-b border-lumia-cream flex items-center gap-2">
            <span class="text-2xl">✨</span> دنیای خوشبوکننده‌ها (بر اساس طبع)
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <NuxtLink
              v-for="cat in fragranceMoods"
              :key="cat.slug"
              :to="`/shop?category=${cat.slug}`"
              class="group flex flex-col items-center p-5 rounded-2xl bg-lumia-cream/20 hover:bg-lumia-cream/50 transition-all duration-300 border border-transparent hover:border-lumia-gold/20"
            >
              <div class="w-16 h-16 rounded-full bg-white flex items-center justify-center text-3xl shadow-sm group-hover:scale-110 transition-transform duration-300">
                {{ cat.icon }}
              </div>
              <span class="font-semibold text-sm mt-3 text-lumia-dark">{{ cat.label }}</span>
              <span class="text-xxs text-base-content/50 mt-1 text-center leading-relaxed">{{ cat.desc }}</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Hygiene moods -->
        <div class="p-8 rounded-3xl bg-white border border-lumia-cream shadow-sm hover:shadow-md transition-shadow">
          <h3 class="text-xl font-bold mb-6 text-lumia-dark pb-3 border-b border-lumia-cream flex items-center gap-2">
            <span class="text-2xl">🧴</span> محصولات بهداشتی (بر اساس روتین)
          </h3>
          <div class="grid grid-cols-3 gap-3">
            <NuxtLink
              v-for="cat in hygieneMoods"
              :key="cat.slug"
              :to="`/shop?category=${cat.slug}`"
              class="group flex flex-col items-center p-4 rounded-2xl bg-lumia-cream/20 hover:bg-lumia-cream/50 transition-all duration-300 border border-transparent hover:border-lumia-gold/20"
            >
              <div class="w-14 h-14 rounded-full bg-white flex items-center justify-center text-2xl shadow-sm group-hover:scale-110 transition-transform duration-300">
                {{ cat.icon }}
              </div>
              <span class="font-semibold text-xs mt-3 text-lumia-dark text-center">{{ cat.label }}</span>
              <span class="text-xxs text-base-content/50 mt-1 text-center leading-tight">{{ cat.desc }}</span>
            </NuxtLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Featured Products Slider -->
    <section class="py-16 md:py-24 bg-white border-y border-lumia-cream">
      <div class="container-lumia">
        <div class="flex flex-col md:flex-row md:items-end justify-between mb-12">
          <div class="text-right">
            <h2 class="section-title text-3xl font-bold">پرفروش‌ترین و محبوب‌ترین‌ها</h2>
            <div class="w-20 h-0.5 bg-lumia-gold my-3"></div>
            <p class="section-subtitle mb-0 text-sm text-base-content/70">محبوب‌ترین و پرطرفدارترین انتخاب‌های همراهان لومیا بیوتی</p>
          </div>
          <NuxtLink to="/shop" class="btn btn-ghost text-lumia-gold hover:bg-lumia-cream/30 rounded-full mt-4 md:mt-0">
            مشاهده کل کاتالوگ ←
          </NuxtLink>
        </div>

        <div v-if="pending" class="grid grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="i in 4" :key="i" class="skeleton h-80 rounded-3xl" />
        </div>
        
        <!-- Smooth Carousel Slider -->
        <div v-else class="relative group">
          <!-- Horizontal Scroll Container -->
          <div class="flex gap-6 overflow-x-auto pb-6 scrollbar-hide snap-x scroll-smooth -mx-4 px-4 md:mx-0 md:px-0">
            <div
              v-for="product in featured"
              :key="product.id"
              class="w-[260px] sm:w-[280px] shrink-0 snap-start"
            >
              <ProductCard :product="product" show-quick-add />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Instagram Social Proof -->
    <InstagramGallery />
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types'

const { apiFetch } = useApi()
const config = useRuntimeConfig()

useSeoMeta({
  title: 'لومیا بیوتی | فروشگاه آنلاین آرایشی، بهداشتی و خوش‌بوکننده لوکس',
  description: 'خرید اینترنتی انواع عطر و ادکلن‌های اصل، محصولات مراقبت پوست و مو با ارسال مطمئن به سراسر ایران در لومیا بیوتی.',
  ogTitle: 'لومیا بیوتی — رایحه‌ای که امضای توست',
  ogDescription: 'رایحه‌ای که امضای توست؛ روتینی که پوستت لایق آن است. خرید اینترنتی عطر و محصولات مراقبتی اصل.',
  ogUrl: config.public.siteUrl,
  ogImage: `${config.public.siteUrl}/images/hero_banner.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: 'لومیا بیوتی | عطر و مراقبت پوست اصل',
  twitterDescription: 'خرید اینترنتی عطر اصل، محصولات پوست و مو با ارسال سریع در ایران.',
})

useSchemaOrg([
  defineWebSite({
    name: 'لومیا بیوتی',
    url: config.public.siteUrl,
    description: 'فروشگاه آنلاین محصولات آرایشی، بهداشتی و عطر اصل با ارسال سریع در سراسر ایران',
    inLanguage: 'fa-IR',
  }),
  defineOrganization({
    name: 'لومیا بیوتی',
    url: config.public.siteUrl,
    logo: `${config.public.siteUrl}/logo.svg`,
    description: 'فروشگاه آنلاین محصولات آرایشی، بهداشتی و عطر لوکس اصل',
    sameAs: [
      'https://www.instagram.com/lumia.beauty',
    ],
  }),
])

const trustBadges = [
  {
    icon: `<svg class="w-6 h-6 text-lumia-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>`,
    title: 'تضمین ۱۰۰٪ اصالت کالا',
    desc: 'ضمانت بازگشت و تاییدیه اصالت کالا'
  },
  {
    icon: `<svg class="w-6 h-6 text-lumia-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/></svg>`,
    title: 'ارسال فوق‌سریع و بهداشتی',
    desc: 'بسته‌بندی ایمن ضدعفونی شده'
  },
  {
    icon: `<svg class="w-6 h-6 text-lumia-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>`,
    title: 'مشاوره انتخاب عطر و روتین',
    desc: 'پشتیبانی رایگان متخصصان پوست و رایحه'
  },
  {
    icon: `<svg class="w-6 h-6 text-lumia-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>`,
    title: 'درگاه پرداخت امن زرین‌پال',
    desc: 'پرداخت آنلاین سریع با تمامی کارت‌ها'
  }
]

const fragranceMoods = [
  { label: 'عطرهای خنک', slug: 'cool-perfumes', icon: '🌿', desc: 'رایحه‌های سبک و مرکباتی' },
  { label: 'عطرهای شیرین', slug: 'sweet-perfumes', icon: '🌸', desc: 'نت‌های گلی و وانیلی' },
  { label: 'عطرهای گرم', slug: 'warm-perfumes', icon: '🔥', desc: 'رایحه‌های شرقی و ادویه‌ای' },
  { label: 'عطرهای تلخ', slug: 'bitter-perfumes', icon: '🪵', desc: 'رایحه‌های چوبی و چرمی' },
]

const hygieneMoods = [
  { label: 'روتین پوست', slug: 'skin-care', icon: '✨', desc: 'آبرسان، شوینده و تقویت‌کننده' },
  { label: 'مراقبت مو', slug: 'hair-care', icon: '💆‍♀️', desc: 'تقویت‌کننده و ماسک مو' },
  { label: 'بهداشت شخصی', slug: 'personal-hygiene', icon: '🧼', desc: 'بادی‌اسپلش و تمیزکننده بدن' },
]

const { data: featured, pending } = await useAsyncData('featured', () =>
  apiFetch<Product[]>('/products/featured/'),
)

useSeoMeta({
  title: 'لومیا بیوتی | خرید آنلاین عطر نیش، ادکلن اصل و مراقبت از پوست',
  description: 'فروشگاه اینترنتی لومیا بیوتی، عرضه‌کننده لوکس‌ترین عطرهای نیش، ادکلن‌های اصل، و محصولات اورجینال مراقبت از پوست شامل آبرسان، روتین پوست و محصولات ضد حساسیت.',
})

useSchemaOrg([
  defineWebSite({
    name: 'لومیا بیوتی',
  }),
  defineWebPage(),
])
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.text-xxs {
  font-size: 0.7rem;
}
</style>
