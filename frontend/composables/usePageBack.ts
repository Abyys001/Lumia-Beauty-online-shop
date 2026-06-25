export interface PageBackTarget {
  mode: 'link' | 'history'
  to?: string
  label: string
}

const PARENT_LABELS: Record<string, string> = {
  '/': 'بازگشت به خانه',
  '/shop': 'بازگشت به فروشگاه',
  '/blog': 'بازگشت به مجله',
  '/account': 'بازگشت به حساب کاربری',
  '/checkout': 'بازگشت به پرداخت',
  '/admin': 'بازگشت به داشبورد',
  '/admin/products': 'بازگشت به محصولات',
  '/admin/categories': 'بازگشت به دسته‌بندی‌ها',
  '/admin/brands': 'بازگشت به برندها',
  '/admin/orders': 'بازگشت به سفارشات',
  '/admin/inventory': 'بازگشت به انبار',
  '/admin/users': 'بازگشت به کاربران',
  '/admin/coupons': 'بازگشت به کدهای تخفیف',
  '/admin/reviews': 'بازگشت به نظرات',
  '/admin/blog': 'بازگشت به وبلاگ',
  '/admin/instagram': 'بازگشت به اینستاگرام',
  '/admin/cms': 'بازگشت به صفحه اصلی',
  '/admin/settings': 'بازگشت به تنظیمات',
  '/admin/sms/dashboard': 'بازگشت به داشبورد SMS',
}

const ROUTE_RULES: Array<{ test: (path: string) => boolean; to: string; label: string }> = [
  { test: p => /^\/shop\/[^/]+$/.test(p), to: '/shop', label: 'بازگشت به فروشگاه' },
  { test: p => /^\/blog\/[^/]+$/.test(p), to: '/blog', label: 'بازگشت به مجله' },
  { test: p => /^\/account\/orders\/[^/]+$/.test(p), to: '/account', label: 'بازگشت به حساب کاربری' },
  { test: p => p === '/checkout', to: '/', label: 'بازگشت به خانه' },
  { test: p => p === '/checkout/success', to: '/account', label: 'بازگشت به حساب کاربری' },
  { test: p => p === '/checkout/failed', to: '/checkout', label: 'بازگشت به پرداخت' },
  { test: p => p === '/auth', to: '/', label: 'بازگشت به خانه' },
  {
    test: p => p.startsWith('/admin/settings/') && p !== '/admin/settings',
    to: '/admin/settings',
    label: 'بازگشت به تنظیمات',
  },
]

const ROOT_NO_BACK = new Set(['/', '/admin'])

function parentPath(path: string): string {
  const segments = path.split('/').filter(Boolean)
  if (segments.length <= 1) return '/'
  segments.pop()
  return '/' + segments.join('/')
}

function labelFor(target: string): string {
  return PARENT_LABELS[target] ?? 'بازگشت'
}

function matchKnownRoute(path: string): PageBackTarget | null {
  for (const rule of ROUTE_RULES) {
    if (rule.test(path)) {
      return { mode: 'link', to: rule.to, label: rule.label }
    }
  }
  return null
}

function normalizePath(path: string): string {
  if (path.length > 1 && path.endsWith('/')) return path.slice(0, -1)
  return path
}

function resolvePageBack(path: string, meta: Record<string, unknown>): PageBackTarget | null {
  path = normalizePath(path)
  if (meta.hideBack) return null

  const explicit = meta.back as { to: string; label?: string } | undefined
  if (explicit?.to) {
    return {
      mode: 'link',
      to: explicit.to,
      label: explicit.label ?? 'بازگشت',
    }
  }

  if (ROOT_NO_BACK.has(path)) return null

  const known = matchKnownRoute(path)
  if (known) return known

  const parent = parentPath(path)
  if (parent && parent !== path) {
    return {
      mode: 'link',
      to: parent,
      label: labelFor(parent),
    }
  }

  if (import.meta.client && window.history.length > 1) {
    return { mode: 'history', label: 'بازگشت' }
  }

  return null
}

export function usePageBack() {
  const route = useRoute()

  const back = computed(() => resolvePageBack(route.path, route.meta))

  return { back }
}
