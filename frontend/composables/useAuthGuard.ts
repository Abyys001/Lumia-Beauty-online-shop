export async function ensureAuthenticated(): Promise<boolean> {
  const auth = useAuthStore()

  if (import.meta.client && !auth.hydrated) {
    await auth.hydrateSession()
  }

  if (auth.isAuthenticated) {
    return true
  }

  const route = useRoute()
  await navigateTo({
    path: '/auth',
    query: { redirect: route.fullPath },
  })
  return false
}
