const BROWSERS: [string, string][] = [
  ['Edg/', 'Edge'],
  ['OPR/', 'Opera'],
  ['Chrome/', 'Chrome'],
  ['Firefox/', 'Firefox'],
  ['Safari/', 'Safari'],
]

const PLATFORMS: [string, string][] = [
  ['Android', 'اندروید'],
  ['iPhone', 'آیفون'],
  ['iPad', 'آیپد'],
  ['Windows', 'ویندوز'],
  ['Mac', 'مک'],
  ['Linux', 'لینوکس'],
]

/**
 * A label the customer will recognise in their device list. The server derives
 * the same thing from the User-Agent; sending it explicitly just lets the
 * browser's own `userAgentData` win where it exists.
 */
export function describeThisDevice(): string {
  if (!import.meta.client) return ''
  const ua = navigator.userAgent || ''
  const browser = BROWSERS.find(([needle]) => ua.includes(needle))?.[1] ?? ''
  const platform = PLATFORMS.find(([needle]) => ua.includes(needle))?.[1] ?? ''
  if (browser && platform) return `${browser} روی ${platform}`
  return browser || platform || 'دستگاه ناشناس'
}
