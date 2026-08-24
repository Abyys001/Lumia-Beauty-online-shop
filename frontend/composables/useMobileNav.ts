export function useMobileNav() {
  // useState, not a module-level ref: a module ref is shared by every SSR request.
  const open = useState('mobile-nav-open', () => false)

  function openNav() {
    open.value = true
  }

  function closeNav() {
    open.value = false
  }

  function toggleNav() {
    open.value = !open.value
  }

  return { open, openNav, closeNav, toggleNav }
}
