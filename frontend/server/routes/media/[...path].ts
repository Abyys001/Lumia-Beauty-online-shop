import { joinURL } from 'ufo'

/**
 * Serve Django uploads from the frontend origin.
 *
 * API payloads are normalized to relative `/media/...` paths (composables/useMediaUrl.ts),
 * so the browser always asks this origin for them. nginx and the Liara edge proxy
 * answer first in production; this handler is what makes dev — and any deployment
 * whose edge rules are missing or misordered — serve images instead of 404s.
 */
export default defineEventHandler(async (event) => {
  const path = getRouterParam(event, 'path') || ''
  setResponseHeader(event, 'cache-control', 'public, max-age=604800')
  try {
    return await proxyRequest(event, joinURL(backendOrigin(), 'media', path))
  } catch {
    // An <img> must never fall through to the HTML error page.
    setResponseStatus(event, 502)
    return ''
  }
})
