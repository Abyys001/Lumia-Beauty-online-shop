import { normalizeMediaUrlsInPayload } from '~/composables/useMediaUrl'
import { isAccessTokenExpired } from '~/utils/jwt'
import { resolveClientApiBase } from '~/utils/apiBase'

export { isAccessTokenExpired, isUnauthorizedError } from '~/utils/jwt'



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



export function extractApiError(error: unknown, fallback: string): string {

  const err = error as {

    statusCode?: number

    data?: Record<string, unknown> & { message?: string; detail?: string | string[] }

  }

  const detail = err.data?.detail

  if (typeof detail === 'string' && detail) return detail

  if (Array.isArray(detail) && detail.length) return detail.join(' ')

  if (err.data?.message) return err.data.message

  // A DRF 400 carries per-field lists and no `detail` at all; without this the
  // caller would report a generic failure and hide the real reason.

  for (const value of Object.values(err.data ?? {})) {

    if (typeof value === 'string' && value) return value

    if (Array.isArray(value) && typeof value[0] === 'string') return value[0]

  }

  if (err.statusCode === 401) {

    return 'نشست شما منقضی شده — دوباره وارد شوید'

  }

  return fallback

}

function createSessionExpiredError(): Error & { statusCode: number } {
  const error = new Error('نشست منقضی شده') as Error & { statusCode: number }
  error.statusCode = 401
  return error
}

export function useApi() {

  const config = useRuntimeConfig()



  const apiFetch = async <T>(url: string, options: Parameters<typeof $fetch<T>>[1] = {}) => {

    const auth = useAuthStore()

    const headers: Record<string, string> = {

      ...(options.headers as Record<string, string> || {}),

    }



    if (import.meta.client && auth.accessToken && isAccessTokenExpired(auth.accessToken)) {
      const refreshed = await auth.refreshAccessToken()
      if (!refreshed) {
        auth.logout(false)
        const reclaimed = await auth.tryDeviceLogin()
        if (!reclaimed) {
          auth.logout()
          if (url.startsWith('/admin/')) {
            await navigateTo({ path: '/auth', query: { redirect: useRoute().fullPath } })
          }
          throw createSessionExpiredError()
        }
      }
    }



    if (auth.accessToken && !isAccessTokenExpired(auth.accessToken)) {

      headers.Authorization = `Bearer ${auth.accessToken}`

    }



    let baseURL = resolveClientApiBase(config.public.apiBase)

    if (import.meta.server) {

      baseURL = process.env.NUXT_API_INTERNAL_URL || 'http://backend:8000/api'

    }



    const doFetch = () => $fetch<T>(url, {

      baseURL,

      ...options,

      headers,

      credentials: import.meta.client ? 'include' : options.credentials,

      onResponse(ctx) {

        if (ctx.response._data !== undefined && ctx.response._data !== null) {

          ctx.response._data = normalizeMediaUrlsInPayload(ctx.response._data)

        }

        if (typeof options.onResponse === 'function') {

          options.onResponse(ctx)

        }

      },

    })



    try {

      return await doFetch()

    } catch (error: unknown) {

      const err = error as { statusCode?: number }

      if (import.meta.client && err.statusCode === 401 && (auth.refreshToken || auth.device)) {

        const recovered = await auth.refreshAccessToken() || await auth.tryDeviceLogin()

        if (recovered && auth.accessToken) {

          headers.Authorization = `Bearer ${auth.accessToken}`

          return await doFetch()

        }

        auth.logout()

      }

      throw error

    }

  }



  return { apiFetch, formatPrice, formatDate, isAccessTokenExpired, extractApiError }
}


