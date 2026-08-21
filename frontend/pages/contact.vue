<template>
  <div class="py-16 md:py-24 bg-lumia-light/30">
    <div class="container-lumia max-w-4xl">
      <!-- Title -->
      <div class="text-center mb-12 md:mb-16">
        <span class="text-xs uppercase tracking-widest text-lumia-gold font-bold">همواره پاسخگوی شما هستیم</span>
        <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black text-lumia-dark mt-2">تماس با لومیا بیوتی</h1>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-4" />
        <p class="text-base-content/70 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          برای مشاوره خرید، پیگیری سفارش یا هر سوالی، از طریق یکی از کانال‌های زیر با ما در ارتباط باشید.
        </p>
      </div>

      <!-- Social Channels -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-5 mb-10">
        <a
          v-for="channel in channels"
          :key="channel.id"
          :href="channel.url"
          target="_blank"
          rel="noopener noreferrer"
          class="group flex flex-col items-center text-center bg-white rounded-3xl border border-lumia-cream p-6 md:p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-transparent"
          :aria-label="channel.label"
        >
          <div
            class="flex items-center justify-center w-16 h-16 rounded-2xl text-white transition-transform duration-300 group-hover:scale-105"
            :style="{ backgroundColor: channel.color }"
          >
            <component :is="iconMap[channel.id]" />
          </div>
          <h2 class="text-base font-bold text-lumia-dark mt-4">{{ channel.label }}</h2>
          <p class="text-xs text-base-content/60 mt-1">{{ channel.subtitle }}</p>
          <span
            class="inline-flex items-center gap-1.5 mt-4 text-xs font-bold transition-colors duration-300"
            :style="{ color: channel.color }"
          >
            شروع گفتگو
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 rotate-180" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </span>
        </a>
      </div>

      <!-- Secondary Info -->
      <div class="bg-white rounded-3xl border border-lumia-cream shadow-sm p-6 md:p-8">
        <h2 class="text-lg font-bold text-lumia-dark border-b border-lumia-cream pb-3 mb-5">سایر راه‌های ارتباطی</h2>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div class="flex items-start gap-3">
            <span class="text-xl mt-0.5" aria-hidden="true">💬</span>
            <div>
              <h3 class="font-bold text-sm text-lumia-dark">پیامک (SMS)</h3>
              <a
                :href="`sms:${smsPhone}`"
                class="block text-xs text-base-content/70 mt-1 dir-ltr text-right hover:text-lumia-gold transition-colors"
              >{{ smsPhone }}</a>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <span class="text-xl mt-0.5" aria-hidden="true">📞</span>
            <div>
              <h3 class="font-bold text-sm text-lumia-dark">تلفن پشتیبانی</h3>
              <a
                :href="`tel:${smsPhone}`"
                class="block text-xs text-base-content/70 mt-1 dir-ltr text-right hover:text-lumia-gold transition-colors"
              >{{ smsPhone }}</a>
              <p class="text-xs text-base-content/50 mt-1">پاسخگو: {{ personName }}</p>
            </div>
          </div>
          <div class="flex items-start gap-3">
            <span class="text-xl mt-0.5" aria-hidden="true">⏰</span>
            <div>
              <h3 class="font-bold text-sm text-lumia-dark">ساعات پاسخگویی</h3>
              <p class="text-xs text-base-content/70 mt-1 leading-relaxed">
                همه‌روزه ۱۰:۰۰ تا ۲۲:۰۰
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import type { SocialChannel } from '~/composables/useSocialLinks'
import type { StoreContact } from '~/types'

const { channels: staticChannels } = useSocialLinks()
const { apiFetch } = useApi()
const { data: contact } = await usePublicData(
  'store-contact',
  () => apiFetch<StoreContact>('/store/contact/'),
  {
    default: () => ({ contact_person_name: '', contact_sms_phone: '', contact_telegram: '', contact_whatsapp: '', contact_bale: '' }),
  },
)

const whatsappFallback = staticChannels.find((c) => c.id === 'whatsapp')!
const telegramFallback = staticChannels.find((c) => c.id === 'telegram')!
const instagramChannel = staticChannels.find((c) => c.id === 'instagram')!

function handleOf(value: string | undefined, fallback: string): string {
  const v = (value || '').trim().replace(/^@/, '')
  return v || fallback
}

/** Convert a local Iranian mobile (09…) to international form (98…). */
function toInternational(value: string): string {
  const d = value.replace(/\D/g, '')
  if (d.startsWith('98')) return d
  if (d.startsWith('0')) return `98${d.slice(1)}`
  return d
}

const smsPhone = computed(() => contact.value?.contact_sms_phone?.trim() || '09166099383')
const personName = computed(() => contact.value?.contact_person_name?.trim() || 'خانم قراچه')

const channels = computed<SocialChannel[]>(() => {
  const list: SocialChannel[] = []
  if (contact.value?.contact_whatsapp?.trim()) {
    const digits = contact.value.contact_whatsapp.replace(/\D/g, '')
    list.push({ ...whatsappFallback, url: `https://wa.me/${digits}`, subtitle: `پاسخگویی سریع — ${digits}` })
  } else {
    list.push(whatsappFallback)
  }
  if (contact.value?.contact_telegram?.trim()) {
    list.push({ ...telegramFallback, url: `https://t.me/${handleOf(contact.value.contact_telegram, '')}` })
  } else {
    list.push(telegramFallback)
  }
  const baleHandle = handleOf(contact.value?.contact_bale, '')
  list.push({
    id: 'bale',
    label: 'بله',
    subtitle: baleHandle ? `@${baleHandle}` : `پیام در بله — ${smsPhone.value}`,
    // Bale resolves both a username and an international phone number.
    url: baleHandle ? `https://bale.me/${baleHandle}` : `https://bale.me/+${toInternational(smsPhone.value)}`,
    color: '#00B8A9',
    hoverColor: '#009a8e',
  })
  list.push({
    id: 'sms',
    label: 'پیامک (SMS)',
    subtitle: smsPhone.value,
    url: `sms:${smsPhone.value}`,
    color: '#6B7B8C',
    hoverColor: '#586675',
  })
  list.push(instagramChannel)
  return list
})

const iconMap: Record<SocialChannel['id'], () => ReturnType<typeof h>> = {
  whatsapp: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', class: 'w-8 h-8' }, [
      h('path', {
        d: 'M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z',
      }),
    ]),
  telegram: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', class: 'w-8 h-8' }, [
      h('path', {
        d: 'M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z',
      }),
    ]),
  instagram: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', class: 'w-8 h-8' }, [
      h('path', {
        d: 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z',
      }),
    ]),
  sms: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', class: 'w-8 h-8' }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        d: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z',
      }),
    ]),
  bale: () =>
    h('svg', { viewBox: '0 0 24 24', fill: 'currentColor', class: 'w-8 h-8' }, [
      h('path', {
        d: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1.4 14.3h-2.3V7.9h2.3v8.4zm4.1.5c-2.5 0-4.1-1.5-4.1-3.8 0-2.2 1.6-3.8 4.1-3.8s4.1 1.6 4.1 3.8c0 2.3-1.6 3.8-4.1 3.8zm0-1.9c1.2 0 1.9-.8 1.9-1.9 0-1.1-.7-1.9-1.9-1.9s-1.9.8-1.9 1.9c0 1.1.7 1.9 1.9 1.9z',
      }),
    ]),
}

useSeoMeta({
  title: 'تماس با ما | لومیا بیوتی',
  description: 'ارتباط با لومیا بیوتی از طریق واتس‌اپ، تلگرام، بله، پیامک و اینستاگرام. مشاوره رایگان انتخاب عطر و روتین پوست.',
})
</script>
