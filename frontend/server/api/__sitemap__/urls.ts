export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const apiInternal = (config.apiInternal as string) || config.public.apiBase
  const siteUrl = (config.public.siteUrl as string).replace(/\/$/, '')

  try {
    const apiUrls = await $fetch<Array<{
      loc: string
      lastmod?: string
      changefreq?: string
      priority?: number
    }>>(`${apiInternal}/sitemap-urls/`)

    return apiUrls.map((entry) => ({
      loc: entry.loc.replace(/^https?:\/\/[^/]+/, siteUrl),
      lastmod: entry.lastmod,
      changefreq: entry.changefreq as 'daily' | 'weekly' | 'monthly' | undefined,
      priority: entry.priority,
    }))
  } catch {
    // Backend unavailable — minimal fallback so /sitemap.xml still responds
    return [
      { loc: `${siteUrl}/`, changefreq: 'daily', priority: 1.0 },
      { loc: `${siteUrl}/shop`, changefreq: 'daily', priority: 0.9 },
      { loc: `${siteUrl}/blog`, changefreq: 'weekly', priority: 0.8 },
    ]
  }
})
