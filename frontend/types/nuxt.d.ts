declare module '#app' {
  interface PageMeta {
    hideBack?: boolean
    back?: { to: string; label?: string }
  }
}

export {}
