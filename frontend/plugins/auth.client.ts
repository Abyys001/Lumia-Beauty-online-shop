export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.hydrateSession()

  if (auth.isAuthenticated) {
    const wishlist = useWishlistStore()
    try {
      await wishlist.loadIds()
    } catch {
      wishlist.reset()
    }
  }
})
