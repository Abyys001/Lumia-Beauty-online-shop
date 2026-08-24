import type { StoreContact } from '~/types'

export interface SocialChannel {
  id: 'whatsapp' | 'telegram' | 'instagram' | 'bale' | 'sms'
  label: string
  subtitle: string
  url: string
  color: string
  hoverColor: string
}

/** Shown only until the store contact settings arrive, and for channels the seller left blank. */
const FALLBACK_CHANNELS: SocialChannel[] = [
  {
    id: 'whatsapp',
    label: 'واتس‌اپ',
    subtitle: 'پاسخگویی سریع و مشاوره خرید',
    url: 'https://wa.me/989166099383',
    color: '#25D366',
    hoverColor: '#1da851',
  },
  {
    id: 'telegram',
    label: 'تلگرام',
    subtitle: 'ارتباط مستقیم با پشتیبانی',
    url: 'https://t.me/lumiabeauty',
    color: '#229ED9',
    hoverColor: '#1a8bc4',
  },
  {
    id: 'instagram',
    label: 'اینستاگرام',
    subtitle: '@lumia.beauty',
    url: 'https://instagram.com/lumia.beauty',
    color: '#E4405F',
    hoverColor: '#c13584',
  },
]

/** Convert a local Iranian mobile (09…) to international form (98…). */
function toInternational(value: string): string {
  const d = value.replace(/\D/g, '')
  if (!d) return ''
  if (d.startsWith('98')) return d
  if (d.startsWith('0')) return `98${d.slice(1)}`
  return d
}

/**
 * Public contact buttons (footer, floating WhatsApp, contact page).
 * The numbers come from `StoreSettings.contact_*` so the seller can change them
 * in the admin — hardcoding them meant the buttons pointed at a dead number.
 */
export function useSocialLinks() {
  const { apiFetch } = useApi()

  // Same key as the contact page, so the payload is fetched once per request.
  const { data: contact } = useAsyncData<StoreContact | null>(
    'store-contact',
    () => apiFetch<StoreContact>('/store/contact/').catch(() => null),
    { default: () => null },
  )

  const channels = computed<SocialChannel[]>(() =>
    FALLBACK_CHANNELS.map((channel) => {
      if (channel.id === 'whatsapp') {
        const wa = toInternational(contact.value?.contact_whatsapp || '')
        return wa ? { ...channel, url: `https://wa.me/${wa}` } : channel
      }
      if (channel.id === 'telegram') {
        const tg = (contact.value?.contact_telegram || '').trim().replace(/^@/, '')
        return tg ? { ...channel, url: `https://t.me/${tg}`, subtitle: `@${tg}` } : channel
      }
      return channel
    }),
  )

  const whatsapp = computed(() => channels.value.find(c => c.id === 'whatsapp')!)

  return { channels, whatsapp, contact }
}
