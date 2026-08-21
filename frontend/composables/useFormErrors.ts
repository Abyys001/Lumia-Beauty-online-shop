/**
 * Turns a DRF error response into per-field messages the form can render.
 *
 * DRF answers a failed `POST` with `{"field": ["message"], ...}`, a bare
 * `{"detail": "message"}`, or `{"non_field_errors": [...]}` — and a crashed
 * request has no body at all. Reading only `detail` (the previous approach)
 * silently swallowed every field error and left the user staring at a generic
 * "something went wrong", so parse all four shapes here, once.
 */

const NETWORK_ERROR = 'ارتباط با سرور برقرار نشد. اتصال اینترنت خود را بررسی کنید و دوباره تلاش کنید.'
const SERVER_ERROR = 'خطای سرور. لطفاً چند لحظه بعد دوباره تلاش کنید. اگر تکرار شد با پشتیبانی تماس بگیرید.'

type ApiError = {
  data?: unknown
  statusCode?: number
  status?: number
}

/** DRF sends `["msg"]` for most fields but a bare string for some. */
function firstMessage(value: unknown): string {
  if (Array.isArray(value)) {
    const first = value.find(v => typeof v === 'string' && v)
    return typeof first === 'string' ? first : ''
  }
  if (typeof value === 'string') return value
  // Nested serializers answer with an object of their own field errors.
  if (value && typeof value === 'object') {
    for (const nested of Object.values(value as Record<string, unknown>)) {
      const message = firstMessage(nested)
      if (message) return message
    }
  }
  return ''
}

export function useFormErrors(labels: Record<string, string> = {}) {
  const fieldErrors = reactive<Record<string, string>>({})
  const generalError = ref('')

  const hasErrors = computed(
    () => !!generalError.value || Object.values(fieldErrors).some(Boolean),
  )

  /** Every message at once, labelled — for the summary box above the submit button. */
  const summary = computed(() => {
    const lines = Object.entries(fieldErrors)
      .filter(([, message]) => !!message)
      .map(([field, message]) => {
        const label = labels[field]
        // Server messages usually name the field already ("کد پستی الزامی است") —
        // prefixing those would stutter.
        if (!label || message.startsWith(label)) return message
        return `${label}: ${message}`
      })
    if (generalError.value) lines.unshift(generalError.value)
    return lines
  })

  function clear() {
    for (const key of Object.keys(fieldErrors)) delete fieldErrors[key]
    generalError.value = ''
  }

  function setField(field: string, message: string) {
    fieldErrors[field] = message
  }

  /**
   * Spread an API failure across the form. Returns the name of the first field
   * that got a message, so the caller can focus or scroll to it.
   */
  function setFromApi(error: unknown, fallback = 'درخواست انجام نشد. لطفاً دوباره تلاش کنید.'): string {
    clear()
    const err = (error ?? {}) as ApiError
    const status = err.statusCode ?? err.status ?? 0
    const body = err.data

    if (!body || typeof body !== 'object') {
      // No parseable body: the request never landed, or the server returned an
      // HTML error page. Neither is the customer's fault — don't blame the form.
      generalError.value = !status ? NETWORK_ERROR : status >= 500 ? SERVER_ERROR : fallback
      return ''
    }

    let firstField = ''
    for (const [key, value] of Object.entries(body as Record<string, unknown>)) {
      const message = firstMessage(value)
      if (!message) continue
      if (key === 'detail' || key === 'non_field_errors') {
        generalError.value ||= message
        continue
      }
      fieldErrors[key] = message
      firstField ||= key
    }

    if (!generalError.value && !firstField) {
      generalError.value = status >= 500 ? SERVER_ERROR : fallback
    }
    return firstField
  }

  return { fieldErrors, generalError, hasErrors, summary, clear, setField, setFromApi }
}
