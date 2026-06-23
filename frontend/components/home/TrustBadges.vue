<template>
  <section class="py-8 md:py-10 bg-lumia-dark text-white border-y border-lumia-gold/20">
    <div class="container-lumia">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 text-center">
        <div
          v-for="badge in displayBadges"
          :key="badge.title"
          class="group flex flex-col items-center p-3 md:p-4 transition-transform duration-300 hover:-translate-y-0.5"
        >
          <div class="w-12 h-12 rounded-full bg-lumia-gold/10 border border-lumia-gold/30 text-lumia-gold flex items-center justify-center mb-3 group-hover:bg-lumia-gold group-hover:text-lumia-dark transition-colors duration-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                :d="iconPaths[badge.icon] || iconPaths.shield"
              />
            </svg>
          </div>
          <h4 class="font-semibold text-sm md:text-base text-lumia-gold">
            {{ badge.title }}
          </h4>
          <p v-if="badge.description" class="text-xs text-white/60 mt-1">
            {{ badge.description }}
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { TrustBadge } from '~/types'

const props = defineProps<{
  badges: TrustBadge[]
}>()

const defaultBadges: TrustBadge[] = [
  { icon: 'shield', title: 'تضمین ۱۰۰٪ اصالت کالا', description: 'ضمانت بازگشت و تاییدیه اصالت' },
  { icon: 'shipping', title: 'ارسال فوق‌سریع و بهداشتی', description: 'بسته‌بندی ایمن ضدعفونی شده' },
  { icon: 'consult', title: 'مشاوره انتخاب عطر و روتین', description: 'پشتیبانی رایگان متخصصان' },
  { icon: 'payment', title: 'درگاه پرداخت امن زرین‌پال', description: 'پرداخت آنلاین با تمامی کارت‌ها' },
]

const displayBadges = computed(() => (props.badges?.length ? props.badges : defaultBadges))

const iconPaths: Record<string, string> = {
  shield: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  shipping: 'M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8',
  consult: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
  payment: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z',
}
</script>
