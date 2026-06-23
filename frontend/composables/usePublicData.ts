type AsyncDataOptions<T> = {
  default?: () => T
  watch?: any[]
  lazy?: boolean
  server?: boolean
}

export async function usePublicData<T>(
  key: string,
  handler: () => Promise<T>,
  options: AsyncDataOptions<T> = {},
) {
  const opts: Record<string, unknown> = {}
  if (options.default) opts.default = options.default
  if (options.watch) opts.watch = options.watch
  if (options.lazy !== undefined) opts.lazy = options.lazy
  if (options.server !== undefined) opts.server = options.server

  return useAsyncData(
    key,
    async () => {
      try {
        return await handler()
      } catch {
        return options.default?.() as T
      }
    },
    opts,
  )
}
