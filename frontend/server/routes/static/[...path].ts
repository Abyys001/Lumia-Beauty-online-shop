import { joinURL } from 'ufo'

/** Django's collected static files (admin theme, RTL css) — see routes/media/[...path].ts. */
export default defineEventHandler(async (event) => {
  const path = getRouterParam(event, 'path') || ''
  setResponseHeader(event, 'cache-control', 'public, max-age=604800')
  try {
    return await proxyRequest(event, joinURL(backendOrigin(), 'static', path))
  } catch {
    setResponseStatus(event, 502)
    return ''
  }
})
