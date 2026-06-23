export default defineNuxtRouteMiddleware(() => {
  // Auth tokens live in localStorage — only available on the client.
  if (import.meta.server) return

  const auth = useAuthStore()
  if (!auth.isAuthenticated) {
    auth.loadFromStorage()
  }

  if (!auth.isAuthenticated || !auth.user?.is_staff) {
    return navigateTo('/')
  }
})
