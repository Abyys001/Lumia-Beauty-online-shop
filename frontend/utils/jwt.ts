function decodeJwtExp(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return typeof payload.exp === 'number' ? payload.exp : null
  } catch {
    return null
  }
}

export function isAccessTokenExpired(token: string | null, skewSeconds = 30): boolean {
  if (!token) return true
  const exp = decodeJwtExp(token)
  if (!exp) return false
  return exp <= Math.floor(Date.now() / 1000) + skewSeconds
}

export function isUnauthorizedError(error: unknown): boolean {
  const err = error as { statusCode?: number; message?: string }
  return err.statusCode === 401 || err.message === 'نشست منقضی شده'
}
