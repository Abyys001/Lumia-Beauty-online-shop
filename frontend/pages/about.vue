<template>
  <div class="py-16 md:py-24 bg-lumia-light/30">
    <div class="container-lumia max-w-4xl">
      <!-- Header -->
      <div class="text-center mb-16">
        <span class="text-xs uppercase tracking-widest text-lumia-gold font-bold">داستان یک تمایز لوکس</span>
        <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black text-lumia-dark mt-2">درباره لومیا بیوتی</h1>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-4"></div>
        <p class="text-base-content/70 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          فلسفه لومیا بیوتی، پیوند میان اصالت، سلامت پوست و جادوی رایحه‌های لوکس است. ما ویترینی از برترین برندهای نیش و طراح جهان را برای شما گردآوری کرده‌ایم.
        </p>
      </div>

      <!-- Content Grid -->
      <div class="space-y-16">
        <!-- Story Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
          <div class="space-y-4">
            <h2 class="text-2xl font-bold text-lumia-dark">میراث و اصالت</h2>
            <p class="text-sm text-base-content/80 leading-relaxed text-justify">
              لومیا بیوتی با ایده خلق تجربه‌ای متفاوت از خرید محصولات آرایشی، بهداشتی و عطرهای نیش تأسیس شد. ما بر این باوریم که هر عطر، امضای شخصی شما و هر محصول پوستی، سرمایه‌گذاری برای شادابی آینده شماست. به همین دلیل، در لومیا بیوتی هیچ جایی برای محصولات فاقد تاییدیه یا فیک وجود ندارد.
            </p>
            <p class="text-sm text-base-content/80 leading-relaxed text-justify">
              ارتباط مستقیم ما با نمایندگان اصلی برندهای معتبری چون شنل، دیور، لانیژ، سراوی و تام فورد، این امکان را فراهم ساخته تا محصولات را در کوتاه‌ترین زمان، با شرایط نگهداری استاندارد و ضمانت صددرصدی به دست شما برسانیم.
            </p>
          </div>
          <div class="relative group aspect-square rounded-3xl overflow-hidden shadow-lg border border-lumia-cream">
            <AppImage
              src="/images/hero_banner.png"
              alt="Lumia Beauty Heritage"
              img-class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-lumia-dark/40 to-transparent"></div>
          </div>
        </div>

        <!-- Three Core Pillars -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8">
          <div class="bg-white p-8 rounded-3xl border border-lumia-cream shadow-xs hover:shadow-md transition-all duration-300 text-center space-y-3">
            <span class="text-4xl">💎</span>
            <h3 class="font-bold text-lumia-dark">ضمانت اصالت</h3>
            <p class="text-xs text-base-content/60 leading-relaxed">
              تمامی محصولات لومیا بیوتی دارای هولوگرام رسمی، ضمانت اصالت فیزیکی و فاکتور معتبر شرکتی می‌باشند.
            </p>
          </div>
          <div class="bg-white p-8 rounded-3xl border border-lumia-cream shadow-xs hover:shadow-md transition-all duration-300 text-center space-y-3">
            <span class="text-4xl">🌱</span>
            <h3 class="font-bold text-lumia-dark">فرمولاسیون پاک</h3>
            <p class="text-xs text-base-content/60 leading-relaxed">
              ما در بخش مراقبتی، اولویت را به محصولات فاقد تست حیوانی، فاقد پارابن و دارای تاییدیه متخصصان پوست داده‌ایم.
            </p>
          </div>
          <div class="bg-white p-8 rounded-3xl border border-lumia-cream shadow-xs hover:shadow-md transition-all duration-300 text-center space-y-3">
            <span class="text-4xl">👑</span>
            <h3 class="font-bold text-lumia-dark">مشاوره تخصصی</h3>
            <p class="text-xs text-base-content/60 leading-relaxed">
              تیم پشتیبانی و مشاوره لومیا، متشکل از بیوتی‌تراپیست‌ها و متخصصین عطر، در هر لحظه آماده راهنمایی شماست.
            </p>
          </div>
        </div>

        <!-- Editorial Quote -->
        <div class="bg-lumia-dark text-white p-4 sm:p-6 md:p-8 lg:p-12 rounded-3xl text-center relative overflow-hidden border border-lumia-gold/20">
          <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-lumia-gold/10 rounded-full blur-2xl"></div>
          <div class="absolute -left-10 -top-10 w-40 h-40 bg-lumia-gold/10 rounded-full blur-2xl"></div>
          <span class="text-4xl text-lumia-gold font-serif">“</span>
          <p class="text-base md:text-lg font-medium leading-relaxed italic max-w-xl mx-auto">
            زیبایی حقیقی، بازتابی از تعادل درونی و مراقبت هوشمندانه است. لومیا بیوتی در این مسیر پرفراز و نشیب، همراه و الهام‌بخش شما خواهد بود.
          </p>
          <div class="w-10 h-0.5 bg-lumia-gold mx-auto my-4"></div>
          <span class="text-xs tracking-widest text-lumia-gold font-bold">تیم مدیریت لومیا بیوتی</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'درباره ما | لومیا بیوتی',
  description: 'با لومیا بیوتی، داستان اصالت عطرها و مراقبت‌های بهداشتی لوکس و ارگانیک را بیشتر بشناسید. تعهد ما ضمانت اصالت کالاهاست.',
})
</script>
