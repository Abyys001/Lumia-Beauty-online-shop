import type { StoreContact } from '~/types'

export type PaymentChannelId = 'sms' | 'telegram' | 'whatsapp' | 'bale'

export interface PaymentChannel {
  id: PaymentChannelId
  label: string
  hint: string
  handle: string
  url: string
  color: string
  configured: boolean
}

const EMPTY_CONTACT: StoreContact = {
  contact_person_name: '',
  contact_sms_phone: '',
  contact_telegram: '',
  contact_whatsapp: '',
  contact_bale: '',
}

function cleanHandle(value?: string): string {
  return (value || '').trim().replace(/^@/, '')
}

function digitsOnly(value?: string): string {
  return (value || '').replace(/\D/g, '')
}

/** Convert a local Iranian mobile (09…) to international form (98…). */
function toInternational(value?: string): string {
  const d = digitsOnly(value)
  if (!d) return ''
  if (d.startsWith('98')) return d
  if (d.startsWith('0')) return `98${d.slice(1)}`
  return d
}

/**
 * Contact channels the customer uses to send their purchase code to the seller.
 * Reads the store contact settings once (shared cache key with the contact page).
 */
export function usePaymentChannels() {
  const { apiFetch } = useApi()

  const contactState = useState<StoreContact | null>('store-contact-channels', () => null)

  async function loadContact() {
    if (contactState.value) return contactState.value
    try {
      contactState.value = await apiFetch<StoreContact>('/store/contact/')
    } catch {
      contactState.value = { ...EMPTY_CONTACT }
    }
    return contactState.value
  }

  function buildMessage(purchaseCode: string, total?: number): string {
    const lines = [
      'سلام، می‌خواهم سفارشم را پرداخت کنم.',
      `کد خرید: ${purchaseCode}`,
    ]
    if (total) lines.push(`مبلغ فاکتور: ${total.toLocaleString('fa-IR')} تومان`)
    lines.push('لطفاً شماره کارت را برای من ارسال کنید.')
    return lines.join('\n')
  }

  function buildChannels(purchaseCode: string, total?: number): PaymentChannel[] {
    const contact = contactState.value || EMPTY_CONTACT
    const message = buildMessage(purchaseCode, total)
    const encoded = encodeURIComponent(message)

    const smsPhone = digitsOnly(contact.contact_sms_phone)
    const waPhone = toInternational(contact.contact_whatsapp)
    const tg = cleanHandle(contact.contact_telegram)
    const bale = cleanHandle(contact.contact_bale)

    return [
      {
        id: 'sms',
        label: 'پیامک (SMS)',
        hint: smsPhone ? `ارسال پیامک به ${smsPhone}` : 'شماره پیامک ثبت نشده است',
        handle: smsPhone,
        // `?&body=` is the cross-platform form that both iOS and Android accept.
        url: smsPhone ? `sms:${smsPhone}?&body=${encoded}` : '',
        color: '#6B7B8C',
        configured: !!smsPhone,
      },
      {
        id: 'telegram',
        label: 'تلگرام',
        hint: tg ? `@${tg}` : 'شناسه تلگرام ثبت نشده است',
        handle: tg,
        url: tg ? `https://t.me/${tg}?text=${encoded}` : '',
        color: '#229ED9',
        configured: !!tg,
      },
      {
        id: 'whatsapp',
        label: 'واتس‌اپ',
        hint: waPhone ? `ارسال پیام به ${waPhone}` : 'شماره واتس‌اپ ثبت نشده است',
        handle: waPhone,
        url: waPhone ? `https://wa.me/${waPhone}?text=${encoded}` : '',
        color: '#25D366',
        configured: !!waPhone,
      },
      {
        id: 'bale',
        label: 'بله',
        hint: bale ? `@${bale}` : 'شناسه بله ثبت نشده است',
        handle: bale,
        url: bale ? `https://bale.me/${bale}` : '',
        color: '#00B8A9',
        configured: !!bale,
      },
    ]
  }

  return { contact: contactState, loadContact, buildChannels, buildMessage }
}
