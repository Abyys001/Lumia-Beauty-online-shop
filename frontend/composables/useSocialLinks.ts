export interface SocialChannel {
  id: 'whatsapp' | 'telegram' | 'instagram'
  label: string
  subtitle: string
  url: string
  color: string
  hoverColor: string
}

export function useSocialLinks() {
  const channels: SocialChannel[] = [
    {
      id: 'whatsapp',
      label: 'واتس‌اپ',
      subtitle: 'پاسخگویی سریع و مشاوره خرید',
      url: 'https://wa.me/989121111111',
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

  const whatsapp = channels.find((c) => c.id === 'whatsapp')!

  return { channels, whatsapp }
}
