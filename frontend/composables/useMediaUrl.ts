const INTERNAL_HOSTS = ['backend:8000', 'localhost:8000', '127.0.0.1:8000']

export function normalizeMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null

  if (url.startsWith('/')) return url

  try {
    const parsed = new URL(url)
    if (INTERNAL_HOSTS.includes(parsed.host) || parsed.pathname.startsWith('/media/')) {
      return parsed.pathname + parsed.search
    }
    return url
  } catch {
    return url
  }
}

export function useMediaUrl() {
  return { normalizeMediaUrl }
}
