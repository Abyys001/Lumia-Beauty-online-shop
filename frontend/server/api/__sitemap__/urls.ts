export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const apiInternal = (config.apiInternal as string) || config.public.apiBase
  const siteUrl = config.public.siteUrl

  // Static pages always included
  const staticUrls = [
    { loc: `${siteUrl}/`, changefreq: 'daily', priority: 1.0 },
    { loc: `${siteUrl}/shop`, changefreq: 'daily', priority: 0.9 },
    { loc: `${siteUrl}/blog`, changefreq: 'weekly', priority: 0.8 },
    { loc: `${siteUrl}/about`, changefreq: 'monthly', priority: 0.5 },
    { loc: `${siteUrl}/contact`, changefreq: 'monthly', priority: 0.5 },
  ]

  try {
    const apiUrls = await $fetch<Array<{ loc: string; lastmod?: string; changefreq?: string; priority?: number }>>(
      `${apiInternal}/sitemap-urls/`,
    )
    // Normalise loc: replace any internal host with the public siteUrl
    const dynamic = apiUrls.map((entry) => ({
      loc: entry.loc.replace(/^https?:\/\/[^/]+/, siteUrl),
      lastmod: entry.lastmod,
      changefreq: entry.changefreq as 'daily' | 'weekly' | 'monthly' | undefined,
      priority: entry.priority,
    }))
    return [...staticUrls, ...dynamic]
  } catch {
    return staticUrls
  }
})
