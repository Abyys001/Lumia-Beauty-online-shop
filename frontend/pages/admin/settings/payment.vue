<template>
  <div class="max-w-4xl space-y-4">
    <div v-if="loadError" class="alert alert-error text-sm">{{ loadError }}</div>
    <div v-if="form.is_mock" class="alert alert-warning text-sm">
      حالت Mock فعال است — پرداخت واقعی انجام نمی‌شود و مستقیماً به callback هدایت می‌شود.
    </div>
    <div v-else-if="form.is_sandbox" class="alert alert-info text-sm">
      Sandbox واقعی زرین‌پال — از Merchant ID تستی استفاده کنید.
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else @submit.prevent="save" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-5">
      <h2 class="font-bold text-lumia-dark pb-4 border-b border-base-200">درگاه پرداخت (Zarinpal)</h2>

      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="label-text text-xs block mb-1">Merchant ID</label>
          <input v-model="form.merchant_id" type="text" class="input input-bordered w-full" dir="ltr" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
        </div>
        <div>
          <label class="label-text text-xs block mb-1">ارز</label>
          <select v-model="form.currency" class="select select-bordered w-full">
            <option value="IRR">ریال (IRR)</option>
            <option value="IRT">تومان (IRT)</option>
          </select>
        </div>
      </div>

      <div class="flex flex-wrap gap-6">
        <label class="label cursor-pointer gap-2">
          <input v-model="form.is_sandbox" type="checkbox" class="toggle toggle-warning toggle-sm" />
          <span class="label-text">Sandbox (URL تستی)</span>
        </label>
        <label class="label cursor-pointer gap-2">
          <input v-model="form.is_mock" type="checkbox" class="toggle toggle-sm" />
          <span class="label-text">Mock محلی (بدون HTTP)</span>
        </label>
        <label class="label cursor-pointer gap-2">
          <input v-model="form.enable_api_logging" type="checkbox" class="toggle toggle-sm" />
          <span class="label-text">لاگ API</span>
        </label>
        <label class="label cursor-pointer gap-2">
          <input v-model="form.auto_reconcile" type="checkbox" class="toggle toggle-sm" />
          <span class="label-text">تسویه خودکار</span>
        </label>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">Callback URL (فعلی)</label>
        <input :value="form.callback_url_resolved" type="url" class="input input-bordered w-full input-sm" dir="ltr" readonly />
        <p class="text-xs text-lumia-dark/40 mt-1">این آدرس باید در پنل زرین‌پال ثبت شود.</p>
      </div>

      <div class="pt-4 border-t border-base-200">
        <h3 class="font-semibold text-sm mb-3">OAuth / GraphQL (مرجوعی و گزارش)</h3>
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="label-text text-xs block mb-1">Client ID</label>
            <input v-model="form.client_id" type="text" class="input input-bordered w-full" dir="ltr" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">Client Secret</label>
            <p v-if="form.client_secret_masked" class="text-xs text-base-content/50 mb-1" dir="ltr">{{ form.client_secret_masked }}</p>
            <input v-model="clientSecret" type="password" class="input input-bordered w-full" dir="ltr" autocomplete="new-password" placeholder="برای تغییر وارد کنید" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">Terminal ID</label>
            <input v-model="form.terminal_id" type="text" class="input input-bordered w-full" dir="ltr" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">وضعیت Token</label>
            <span class="badge" :class="form.token_valid ? 'badge-success' : 'badge-ghost'">
              {{ form.token_valid ? 'معتبر' : 'نامعتبر / منقضی' }}
            </span>
          </div>
        </div>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">حداکثر تلاش مجدد API</label>
        <input v-model.number="form.max_retry_attempts" type="number" min="1" max="10" class="input input-bordered w-24" />
      </div>

      <div class="flex flex-wrap gap-2 pt-2">
        <button type="submit" class="btn btn-primary btn-sm" :class="{ loading: saving }">ذخیره</button>
        <button type="button" class="btn btn-outline btn-sm" :class="{ loading: testing }" @click="testConnection">تست اتصال</button>
        <button type="button" class="btn btn-ghost btn-sm" :class="{ loading: loadingSessions }" @click="loadSessions">تراکنش‌ها</button>
        <button type="button" class="btn btn-ghost btn-sm" :class="{ loading: loadingReconcile }" @click="loadReconciliations">تسویه‌ها</button>
        <span v-if="saved" class="text-success text-sm self-center">ذخیره شد</span>
      </div>
      <div v-if="testMessage" class="text-sm" :class="testOk ? 'text-success' : 'text-error'">{{ testMessage }}</div>
      <div v-if="sessionsPreview" class="text-xs bg-base-200 rounded-lg p-3 overflow-auto max-h-40" dir="ltr">
        <pre>{{ sessionsPreview }}</pre>
      </div>
      <div v-if="error" class="alert alert-error text-sm">{{ error }}</div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { ZarinpalSettings } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const saving = ref(false)
const saved = ref(false)
const error = ref('')
const loadError = ref('')
const testing = ref(false)
const testMessage = ref('')
const testOk = ref(false)
const clientSecret = ref('')
const loadingSessions = ref(false)
const loadingReconcile = ref(false)
const sessionsPreview = ref('')

const form = ref<ZarinpalSettings>({
  merchant_id: '',
  is_sandbox: true,
  is_mock: true,
  callback_url: '',
  callback_url_resolved: '',
  currency: 'IRR',
  client_id: '',
  client_secret_masked: '',
  terminal_id: '',
  auto_reconcile: false,
  max_retry_attempts: 3,
  enable_api_logging: true,
  token_valid: false,
  token_expires_at: null,
})

async function load() {
  try {
    form.value = await apiFetch<ZarinpalSettings>('/admin/zarinpal/settings/')
  } catch {
    loadError.value = 'خطا در بارگذاری تنظیمات'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true; saved.value = false; error.value = ''
  try {
    const body: Record<string, unknown> = { ...form.value }
    delete body.client_secret_masked
    delete body.callback_url_resolved
    delete body.token_valid
    delete body.token_expires_at
    if (clientSecret.value) body.client_secret = clientSecret.value
    form.value = await apiFetch<ZarinpalSettings>('/admin/zarinpal/settings/', { method: 'PATCH', body })
    clientSecret.value = ''
    saved.value = true
    setTimeout(() => { saved.value = false }, 3000)
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ذخیره'
  } finally { saving.value = false }
}

async function testConnection() {
  testing.value = true; testMessage.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string; mock?: boolean }>(
      '/admin/zarinpal/settings/test/',
      { method: 'POST' },
    )
    testOk.value = res.success
    testMessage.value = res.message
  } catch (e: unknown) {
    testOk.value = false
    const err = e as { data?: { message?: string; detail?: string } }
    testMessage.value = err.data?.message || err.data?.detail || 'تست ناموفق'
  } finally { testing.value = false }
}

async function loadSessions() {
  loadingSessions.value = true
  try {
    const res = await apiFetch<{ sessions: unknown[] }>('/admin/zarinpal/sessions/')
    sessionsPreview.value = JSON.stringify(res.sessions?.slice(0, 5) ?? [], null, 2)
  } catch (e: unknown) {
    const err = e as { data?: { errors?: { message: string }[] } }
    sessionsPreview.value = err.data?.errors?.[0]?.message || 'خطا در دریافت تراکنش‌ها'
  } finally { loadingSessions.value = false }
}

async function loadReconciliations() {
  loadingReconcile.value = true
  try {
    const res = await apiFetch<{ reconciliations: unknown[] }>('/admin/zarinpal/reconciliations/?status=PAID')
    sessionsPreview.value = JSON.stringify(res.reconciliations?.slice(0, 5) ?? [], null, 2)
  } catch (e: unknown) {
    const err = e as { data?: { errors?: { message: string }[] } }
    sessionsPreview.value = err.data?.errors?.[0]?.message || 'خطا در دریافت تسویه‌ها'
  } finally { loadingReconcile.value = false }
}

onMounted(load)
</script>
