export function formatPrice(price: number): string {
  return new Intl.NumberFormat('fa-IR').format(price) + ' تومان'
}

export function formatDate(date: string): string {
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date))
}

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

export function useApi() {
  const config = useRuntimeConfig()

  const apiFetch = <T>(url: string, options: Parameters<typeof $fetch<T>>[1] = {}) => {
    const auth = useAuthStore()
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    }
    if (auth.accessToken) {
      if (!import.meta.server && isTokenExpired(auth.accessToken)) {
        auth.logout()
      } else {
        headers.Authorization = `Bearer ${auth.accessToken}`
      }
    }

    let baseURL = config.public.apiBase
    if (import.meta.server) {
      baseURL = process.env.NUXT_API_INTERNAL_URL || 'http://backend:8000/api'
    }

    return $fetch<T>(url, {
      baseURL,
      ...options,
      headers,
    })
  }

  return { apiFetch, formatPrice, formatDate }
}

