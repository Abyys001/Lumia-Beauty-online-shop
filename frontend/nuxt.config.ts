// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  ssr: true,

  app: {
    head: {
      htmlAttrs: { lang: 'fa', dir: 'rtl' },
      title: 'لومیا بیوتی | خرید آنلاین عطر نیش، ادکلن اصل و مراقبت از پوست',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'لومیا بیوتی — فروشگاه لوکس خرید آنلاین عطر نیش، ادکلن اصل و محصولات مراقبت از پوست اورجینال، آبرسان و ضد حساسیت. تضمین اصالت و ارسال سریع به سراسر ایران.',
        },
        {
          name: 'keywords',
          content: 'خرید عطر نیش, ادکلن اصل, محصولات مراقبت از پوست, روتین پوست, آبرسان پوست, محصولات ضد حساسیت, خرید لوازم آرایشی اورجینال, لومیا بیوتی',
        },
        { name: 'format-detection', content: 'telephone=no' },
        { property: 'og:locale', content: 'fa_IR' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'لومیا بیوتی' },
        { property: 'og:title', content: 'لومیا بیوتی | خرید آنلاین عطر نیش، ادکلن اصل و مراقبت از پوست' },
        { property: 'og:description', content: 'فروشگاه آنلاین لومیا بیوتی، عرضه‌کننده بهترین عطرهای نیش و محصولات اورجینال مراقبت از پوست با تضمین اصالت کالا.' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32.png' },
        { rel: 'icon', type: 'image/png', sizes: '192x192', href: '/favicon-192.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
        {
          rel: 'stylesheet',
          href: 'https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/Vazirmatn-font-face.css',
        },
      ],
    },
  },

  css: ['~/assets/css/main.css'],

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxt/image',
    '@nuxtjs/i18n',
    '@nuxtjs/sitemap',
    'nuxt-schema-org',
  ],

  runtimeConfig: {
    apiInternal: process.env.NUXT_API_INTERNAL_URL || 'http://localhost/api',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost/api',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost',
    },
  },

  i18n: {
    locales: [{ code: 'fa', language: 'fa-IR', name: 'فارسی', dir: 'rtl' }],
    defaultLocale: 'fa',
    strategy: 'no_prefix',
  },

  image: {
    format: ['webp'],
    quality: 80,
    domains: ['localhost', '127.0.0.1', 'backend', 'backend:8000'],
    alias: {
      'http://localhost': 'http://backend:8000'
    }
  },

  site: {
    url: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost',
    name: 'لومیا بیوتی',
  },

  sitemap: {
    siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost',
    sources: ['/api/__sitemap__/urls'],
    inferStaticPagesFromBuild: false,
    autoLastmod: false,
    exclude: [
      '/account',
      '/account/**',
      '/auth',
      '/cart',
      '/checkout',
      '/checkout/**',
    ],
  },

  nitro: {
    devProxy: {
      '/api': {
        target: process.env.NUXT_API_PROXY || 'http://backend:8000/api',
        changeOrigin: true,
      },
    },
  },

  tailwindcss: {
    configPath: 'tailwind.config.ts',
  },
})
