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

export function useApi() {
  const config = useRuntimeConfig()

  const apiFetch = <T>(url: string, options: Parameters<typeof $fetch<T>>[1] = {}) => {
    const auth = useAuthStore()
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    }
    if (auth.accessToken) {
      headers.Authorization = `Bearer ${auth.accessToken}`
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

