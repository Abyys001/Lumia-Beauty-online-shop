export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.hydrateSession()

  const cart = useCartStore()
  try {
    await cart.fetchCart()
  } catch {
    // Guest or stale session — cart loads on next interaction.
  }

  if (auth.isAuthenticated) {
    const wishlist = useWishlistStore()
    try {
      await wishlist.loadIds()
    } catch {
      wishlist.reset()
    }
  }
})
