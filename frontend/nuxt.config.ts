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
        { name: 'theme-color', content: '#D4AF37' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: 'لومیا بیوتی' },
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
    '@vite-pwa/nuxt',
  ],

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'لومیا بیوتی',
      short_name: 'Lumia',
      description: 'فروشگاه آنلاین محصولات آرایشی، بهداشتی و عطر لوکس',
      theme_color: '#D4AF37',
      background_color: '#1C1A17',
      display: 'standalone',
      lang: 'fa',
      dir: 'rtl',
      start_url: '/',
      scope: '/',
      icons: [
        {
          src: '/favicon-192.png',
          sizes: '192x192',
          type: 'image/png',
          purpose: 'maskable any',
        },
        {
          src: '/favicon-512.png',
          sizes: '512x512',
          type: 'image/png',
          purpose: 'maskable any',
        },
      ],
    },
    workbox: {
      navigateFallback: '/',
      navigateFallbackDenylist: [/^\/admin/, /^\/checkout/, /^\/auth/, /^\/django-admin/],
      globPatterns: ['**/*.{js,css,html,png,svg,ico,webp,woff2}'],
      runtimeCaching: [
        {
          urlPattern: ({ url }) => url.pathname.startsWith('/api/'),
          handler: 'NetworkFirst',
          options: {
            cacheName: 'lumia-api',
            networkTimeoutSeconds: 10,
            expiration: { maxEntries: 50, maxAgeSeconds: 300 },
          },
        },
      ],
    },
    client: {
      installPrompt: true,
    },
    devOptions: {
      enabled: false,
    },
  },

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
    format: ['avif', 'webp'],
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

  vite: {
    server: {
      watch: {
        usePolling: true,
        interval: 300,
      },
      hmr: {
        ...(process.env.NUXT_VITE_CLIENT_PORT && {
          clientPort: parseInt(process.env.NUXT_VITE_CLIENT_PORT),
        }),
      },
    },
  },

  tailwindcss: {
    configPath: 'tailwind.config.ts',
  },
})
