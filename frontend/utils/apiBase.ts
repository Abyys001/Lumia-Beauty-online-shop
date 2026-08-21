/**
 * Resolve the browser-side API base URL.
 *
 * The app is always served from the origin that also proxies `/api` (Nuxt
 * `devProxy` in dev, the edge proxy in production). When the configured base
 * points at the same hostname on a different port — the usual symptom of an
 * `.env` written for one deployment and served from another — rebase it onto
 * the page origin instead of firing requests at a port nothing is listening on.
 */
export function resolveClientApiBase(configured: string): string {
  if (typeof window === 'undefined') return configured
  try {
    const url = new URL(configured, window.location.origin)
    if (url.hostname === window.location.hostname && url.host !== window.location.host) {
      return window.location.origin + url.pathname.replace(/\/$/, '')
    }
    return configured
  } catch {
    return configured
  }
}
