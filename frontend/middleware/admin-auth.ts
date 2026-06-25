export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return

  const auth = useAuthStore()
  if (!auth.hydrated) {
    await auth.hydrateSession()
  }

  if (!auth.isAuthenticated || !auth.user?.is_staff) {
    return navigateTo({
      path: '/auth',
      query: { redirect: to.fullPath },
    })
  }
})
