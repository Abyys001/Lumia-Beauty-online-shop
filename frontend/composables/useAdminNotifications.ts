import type { AdminNotificationsSummary } from '~/types'

export function useAdminNotifications() {
  const summary = ref<AdminNotificationsSummary | null>(null)

  async function fetchSummary() {
    if (!import.meta.client) return
    try {
      const { apiFetch } = useApi()
      summary.value = await apiFetch<AdminNotificationsSummary>('/admin/notifications/summary/')
    } catch {
      // ignore when not staff
    }
  }

  let timer: ReturnType<typeof setInterval> | null = null

  onMounted(() => {
    fetchSummary()
    timer = setInterval(() => {
      if (document.visibilityState === 'visible') fetchSummary()
    }, 60000)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return { summary, fetchSummary }
}
