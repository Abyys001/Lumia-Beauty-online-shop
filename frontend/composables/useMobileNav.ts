const open = ref(false)

export function useMobileNav() {
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
