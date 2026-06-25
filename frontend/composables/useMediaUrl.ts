const INTERNAL_HOST_PATTERN = /^(backend(?::\d+)?|localhost(?::\d+)?|127\.0\.0\.1(?::\d+)?)$/i

function isMediaPath(pathname: string): boolean {
  return pathname.startsWith('/media/') || pathname.startsWith('/static/')
}

export function normalizeMediaUrl(url: string | null | undefined): string | null {
  if (url === null || url === undefined) return null
  if (typeof url !== 'string') return null

  const trimmed = url.trim()
  if (!trimmed || trimmed === 'true' || trimmed === 'false') return null

  if (trimmed.startsWith('/')) return trimmed

  if (trimmed.startsWith('media/') || trimmed.startsWith('static/')) {
    return `/${trimmed}`
  }

  try {
    const parsed = new URL(trimmed)
    if (INTERNAL_HOST_PATTERN.test(parsed.host) || isMediaPath(parsed.pathname)) {
      return parsed.pathname + parsed.search
    }
    return trimmed
  } catch {
    return trimmed
  }
}

function shouldNormalizeString(value: string): boolean {
  if (value.startsWith('/') || value.startsWith('media/') || value.startsWith('static/')) {
    return isMediaPath(value.startsWith('/') ? value : `/${value}`)
  }

  try {
    const parsed = new URL(value)
    return INTERNAL_HOST_PATTERN.test(parsed.host) || isMediaPath(parsed.pathname)
  } catch {
    return false
  }
}

export function normalizeMediaUrlsInPayload<T>(payload: T): T {
  if (payload === null || payload === undefined) return payload

  if (typeof payload === 'string') {
    if (!shouldNormalizeString(payload)) return payload
    return (normalizeMediaUrl(payload) ?? payload) as T
  }

  if (Array.isArray(payload)) {
    return payload.map((item) => normalizeMediaUrlsInPayload(item)) as T
  }

  if (typeof payload === 'object') {
    const normalized: Record<string, unknown> = {}
    for (const [key, value] of Object.entries(payload)) {
      normalized[key] = normalizeMediaUrlsInPayload(value)
    }
    return normalized as T
  }

  return payload
}

export function useMediaUrl() {
  return { normalizeMediaUrl, normalizeMediaUrlsInPayload }
}
