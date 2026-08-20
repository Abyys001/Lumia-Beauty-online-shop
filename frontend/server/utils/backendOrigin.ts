/**
 * Origin that serves Django's /media and /static, resolved per request.
 *
 * `process.env` is read first on purpose. Nuxt only maps runtime config keys to
 * their own env names (`apiInternal` ← `NUXT_API_INTERNAL`), so the value baked
 * into the image at build time would otherwise win over the
 * `NUXT_API_INTERNAL_URL` every deployment actually sets — pointing the proxy at
 * the build machine's backend instead of the server's.
 */
export function backendOrigin(): string {
  const config = useRuntimeConfig()
  const candidate =
    process.env.NUXT_MEDIA_PROXY
    || config.mediaProxy
    || process.env.NUXT_API_INTERNAL_URL
    || config.apiInternal
    || 'http://backend:8000/api'
  return String(candidate).replace(/\/api\/?$/, '').replace(/\/$/, '')
}
