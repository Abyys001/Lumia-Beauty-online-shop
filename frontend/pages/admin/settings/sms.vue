<template>
  <div class="max-w-4xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline inline-block">
      داشبورد SMS →
    </NuxtLink>

    <div v-if="loadError" class="alert alert-error text-sm">{{ loadError }}</div>
    <div
      v-if="status?.runtime_provider === 'mock' || (status?.is_sandbox && isSmsIr)"
      class="alert alert-warning text-sm"
    >
      <div class="space-y-1">
        <p v-if="status?.runtime_provider === 'mock'">
          حالت Mock فعال است — پیامک واقعی ارسال نمی‌شود.
        </p>
        <template v-else-if="status?.is_sandbox">
          <p class="font-semibold">حالت Sandbox فعال است — پیامک واقعی ارسال نمی‌شود و گزارش در SMS.ir ثبت نمی‌شود.</p>
          <p>قالب خودکار: <span dir="ltr">123456</span> / پارامتر <span dir="ltr">Code</span>. کلید Sandbox جدا از Production.</p>
          <p>برای پیامک واقعی: Sandbox خاموش + کلید Production + قالب ۳۹۴۲۱۲.</p>
        </template>
      </div>
    </div>

    <div role="tablist" class="tabs tabs-boxed bg-white p-1 rounded-xl border border-base-200 w-fit flex-wrap">
      <button
        v-for="t in tabs"
        :key="t.id"
        role="tab"
        class="tab"
        :class="{ 'tab-active': activeTab === t.id }"
        @click="activeTab = t.id"
      >
        {{ t.label }}
      </button>
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <!-- Provider tab -->
    <div v-else-if="activeTab === 'provider'" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-5">
      <div class="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-base-200">
        <h2 class="font-bold text-lumia-dark">تنظیمات {{ providerLabel }}</h2>
        <div class="flex items-center gap-2 text-xs">
          <span class="badge" :class="runtimeBadgeClass">
            {{ runtimeLabel }}
          </span>
          <span v-if="status?.is_sandbox && isSmsIr" class="badge badge-warning">Sandbox</span>
        </div>
      </div>

      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="label-text text-xs block mb-1">ارائه‌دهنده</label>
          <select v-model="providerForm.provider_mode" class="select select-bordered w-full" @change="onProviderModeChange">
            <option value="mock">Mock (توسعه)</option>
            <option value="smsir">SMS.ir</option>
            <option value="iranpayamak">IranPayamak</option>
          </select>
        </div>
        <div class="flex items-end gap-4 flex-wrap">
          <label v-if="isSmsIr" class="label cursor-pointer gap-2">
            <input v-model="providerForm.is_sandbox" type="checkbox" class="toggle toggle-warning toggle-sm" />
            <span class="label-text">Sandbox</span>
          </label>
          <label class="label cursor-pointer gap-2">
            <input v-model="providerForm.is_active" type="checkbox" class="toggle toggle-success toggle-sm" />
            <span class="label-text">فعال</span>
          </label>
        </div>
      </div>

      <div>
        <label class="label-text text-xs block mb-1">{{ isIranPayamak ? 'Api-Key' : 'کلید Production' }}</label>
        <p v-if="apiKeyHint" class="text-xs text-base-content/50 mb-1" dir="ltr">کلید فعلی: {{ apiKeyHint }}</p>
        <input
          v-model="providerForm.api_key"
          type="password"
          class="input input-bordered w-full"
          dir="ltr"
          autocomplete="new-password"
          :placeholder="isIranPayamak ? 'Api-Key IranPayamak' : 'کلید Production را کامل paste کنید'"
        />
        <p v-if="isSmsIr" class="text-xs text-base-content/50 mt-1">برای پیامک واقعی با قالب ۳۹۴۲۱۲ — Sandbox خاموش + این کلید</p>
      </div>

      <template v-if="isIranPayamak">
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="label-text text-xs block mb-1">شماره خط (line_number)</label>
            <input v-model="providerForm.line_number" type="text" class="input input-bordered w-full" dir="ltr" placeholder="50002178584000" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">فرمت اعداد</label>
            <select v-model="providerForm.number_format" class="select select-bordered w-full">
              <option value="english">English</option>
              <option value="persian">Persian</option>
            </select>
          </div>
        </div>

        <div class="rounded-xl border border-base-200 p-4 space-y-3">
          <h3 class="font-semibold text-sm">ورود پنل (برای دریافت خطوط — اختیاری)</h3>
          <div class="grid sm:grid-cols-2 gap-3">
            <input v-model="providerForm.panel_username" type="text" class="input input-bordered w-full" dir="ltr" placeholder="نام کاربری پنل" />
            <input v-model="panelPasswordInput" type="password" class="input input-bordered w-full" dir="ltr" autocomplete="new-password" placeholder="رمز عبور پنل" />
          </div>
          <p v-if="panelPasswordHint" class="text-xs text-base-content/50" dir="ltr">رمز فعلی: {{ panelPasswordHint }}</p>
          <div class="flex flex-wrap gap-2 items-center">
            <button type="button" class="btn btn-outline btn-sm" :class="{ loading: loggingIn }" @click="panelLogin">ورود</button>
            <span v-if="status?.has_bearer_token" class="badge badge-success badge-sm">Bearer فعال</span>
          </div>
          <div v-if="loginMessage" class="text-sm" :class="loginOk ? 'text-success' : 'text-warning'">{{ loginMessage }}</div>
          <div v-if="pending2faToken" class="grid sm:grid-cols-2 gap-3 pt-2 border-t border-base-200">
            <input v-model="twoFaCode" type="text" class="input input-bordered w-full" dir="ltr" placeholder="کد 2FA" maxlength="8" />
            <button type="button" class="btn btn-outline btn-sm" :class="{ loading: verifying2fa }" @click="verify2fa">تأیید 2FA</button>
          </div>
        </div>
      </template>

      <template v-if="isSmsIr">
      <div>
        <label class="label-text text-xs block mb-1">کلید Sandbox</label>
        <p v-if="sandboxApiKeyHint" class="text-xs text-base-content/50 mb-1" dir="ltr">کلید فعلی: {{ sandboxApiKeyHint }}</p>
        <input
          v-model="providerForm.sandbox_api_key"
          type="password"
          class="input input-bordered w-full"
          dir="ltr"
          autocomplete="new-password"
          placeholder="کلید Sandbox (اختیاری — فقط برای تست)"
        />
        <p class="text-xs text-base-content/50 mt-1">فقط با Sandbox روشن — قالب خودکار ۱۲۳۴۵۶.</p>
      </div>
      <div>
        <label class="label-text text-xs block mb-1">Base URL</label>
        <input v-model="providerForm.base_url" type="url" class="input input-bordered w-full" dir="ltr" readonly />
        <p class="text-xs text-base-content/50 mt-1">آدرس رسمی SMS.ir — قابل تغییر نیست.</p>
      </div>
      </template>

      <div v-if="isIranPayamak">
        <label class="label-text text-xs block mb-1">Base URL</label>
        <input :value="iranpayamakBaseUrl" type="url" class="input input-bordered w-full" dir="ltr" readonly />
      </div>

      <div v-if="status" class="rounded-xl bg-base-200/40 p-4 text-sm space-y-1">
        <div>اعتبار: {{ status.credit ?? '—' }}<span v-if="status.balance_count != null"> ({{ status.balance_count }} پیامک)</span></div>
        <div v-if="status.balance_details?.length" class="text-xs text-base-content/60 space-y-0.5">
          <div v-for="(d, i) in status.balance_details" :key="i" dir="ltr">
            {{ d.count }} × {{ d.rate }} = {{ d.amount }} تومان
          </div>
        </div>
        <div>آخرین تست: {{ status.last_test_status }} — {{ status.last_test_message || '—' }}</div>
      </div>

      <div class="flex flex-wrap gap-2">
        <button type="button" class="btn btn-primary btn-sm" :class="{ loading: savingProvider }" @click="saveProvider">ذخیره</button>
        <button type="button" class="btn btn-outline btn-sm" :class="{ loading: testing }" @click="testConnection">تست اتصال</button>
      </div>
      <div v-if="testMessage" class="text-sm" :class="testOk ? 'text-success' : 'text-error'">{{ testMessage }}</div>
    </div>

    <!-- Templates tab -->
    <div v-else-if="activeTab === 'templates'" class="space-y-4">
      <div class="flex justify-end">
        <button class="btn btn-primary btn-sm" @click="openTemplateForm()">قالب جدید</button>
      </div>

      <div class="bg-white rounded-2xl border border-base-200 overflow-hidden">
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-xs text-lumia-dark/60">
                <th>نام</th>
                <th>{{ isIranPayamak ? 'Pattern' : 'Template ID' }}</th>
                <th>پارامتر</th>
                <th>پیش‌فرض</th>
                <th>فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tpl in templates" :key="tpl.id">
                <td>{{ tpl.name }}</td>
                <td dir="ltr">{{ isIranPayamak ? (tpl.pattern_code || '—') : (tpl.sms_ir_template_id ?? '—') }}</td>
                <td dir="ltr">{{ tpl.parameter_name }}</td>
                <td><span v-if="tpl.is_default" class="badge badge-primary badge-sm">پیش‌فرض</span></td>
                <td><input type="checkbox" class="toggle toggle-sm toggle-success" :checked="tpl.is_active" @change="toggleTemplate(tpl)" /></td>
                <td class="flex gap-1">
                  <button class="btn btn-ghost btn-xs" @click="openTemplateForm(tpl)">ویرایش</button>
                  <button v-if="!tpl.is_default" class="btn btn-ghost btn-xs text-lumia-gold" @click="setDefault(tpl)">پیش‌فرض</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <dialog ref="templateDialog" class="modal">
        <div class="modal-box max-w-lg">
          <h3 class="font-bold mb-4">{{ editingTemplate?.id ? 'ویرایش قالب' : 'قالب جدید' }}</h3>
          <form class="space-y-3" @submit.prevent="saveTemplate">
            <input v-model="templateForm.name" class="input input-bordered w-full" placeholder="نام" required />
            <input
              v-if="isIranPayamak"
              v-model="templateForm.pattern_code"
              type="text"
              class="input input-bordered w-full"
              dir="ltr"
              placeholder="Pattern UID (مثلاً SJ3FgPrE0C)"
              required
            />
            <input
              v-else
              v-model.number="templateForm.sms_ir_template_id"
              type="number"
              class="input input-bordered w-full"
              dir="ltr"
              placeholder="Template ID"
              required
            />
            <input v-model="templateForm.parameter_name" class="input input-bordered w-full" dir="ltr" placeholder="Parameter name (Code)" required />
            <textarea v-model="templateForm.body_preview" class="textarea textarea-bordered w-full" rows="3" placeholder="پیش‌نمایش: کد تایید شما: {Code}" />
            <div class="rounded-lg bg-base-200/50 p-3 text-sm">
              <span class="text-lumia-dark/50">Preview: </span>{{ templatePreview }}
            </div>
            <div class="modal-action">
              <button type="button" class="btn btn-ghost" @click="closeTemplateForm">انصراف</button>
              <button type="submit" class="btn btn-primary" :class="{ loading: savingTemplate }">ذخیره</button>
            </div>
          </form>
        </div>
        <form method="dialog" class="modal-backdrop"><button>close</button></form>
      </dialog>
    </div>

    <!-- OTP tab -->
    <form v-else-if="activeTab === 'otp'" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-4" @submit.prevent="saveOtp">
      <h2 class="font-bold text-lumia-dark pb-4 border-b border-base-200">تنظیمات OTP</h2>
      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="label-text text-xs">طول OTP (۴–۸)</label>
          <input v-model.number="otpForm.otp_length" type="number" min="4" max="8" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">انقضا (ثانیه)</label>
          <input v-model.number="otpForm.expiry_seconds" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">حداکثر تلاش تأیید</label>
          <input v-model.number="otpForm.max_verify_attempts" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">تأخیر ارسال مجدد (ثانیه)</label>
          <input v-model.number="otpForm.resend_delay_seconds" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">محدودیت درخواست (تعداد)</label>
          <input v-model.number="otpForm.rate_limit_count" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">پنجره محدودیت درخواست (ثانیه)</label>
          <input v-model.number="otpForm.rate_limit_window_seconds" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">محدودیت IP (تعداد)</label>
          <input v-model.number="otpForm.ip_rate_limit_count" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">پنجره IP (ثانیه)</label>
          <input v-model.number="otpForm.ip_rate_limit_window_seconds" type="number" class="input input-bordered w-full" />
        </div>
      </div>
      <button type="submit" class="btn btn-primary btn-sm" :class="{ loading: savingOtp }">ذخیره</button>
    </form>

    <!-- Auth tab -->
    <form v-else class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-4" @submit.prevent="saveAuth">
      <h2 class="font-bold text-lumia-dark pb-4 border-b border-base-200">احراز هویت</h2>
      <div class="flex items-center gap-2 text-sm text-lumia-dark/70">
        <span class="badge badge-success badge-sm">OTP</span>
        تنها روش ورود — ورود با رمز عبور پشتیبانی نمی‌شود.
      </div>
      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="label-text text-xs">Access Token (دقیقه)</label>
          <input v-model.number="authForm.access_token_lifetime_minutes" type="number" class="input input-bordered w-full" />
        </div>
        <div>
          <label class="label-text text-xs">Refresh Token (روز)</label>
          <input v-model.number="authForm.refresh_token_lifetime_days" type="number" class="input input-bordered w-full" />
        </div>
        <div class="sm:col-span-2">
          <label class="label-text text-xs">شماره bypass ادمین</label>
          <input v-model="authForm.admin_bypass_phone" type="tel" class="input input-bordered w-full" dir="ltr" placeholder="09916122680" />
        </div>
      </div>
      <label class="label cursor-pointer justify-start gap-2">
        <input v-model="authForm.rotate_refresh_tokens" type="checkbox" class="checkbox checkbox-sm" />
        <span class="label-text">چرخش Refresh Token</span>
      </label>
      <button type="submit" class="btn btn-primary btn-sm" :class="{ loading: savingAuth }">ذخیره</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import type {
  AuthSettings,
  OtpSettings,
  OtpTemplate,
  SmsProviderSettings,
  SmsProviderStatus,
} from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, extractApiError } = useApi()

const tabs = [
  { id: 'provider', label: 'ارائه‌دهنده' },
  { id: 'templates', label: 'قالب OTP' },
  { id: 'otp', label: 'OTP' },
  { id: 'auth', label: 'احراز هویت' },
] as const

type TabId = typeof tabs[number]['id']

const activeTab = ref<TabId>('provider')
const loading = ref(true)
const status = ref<SmsProviderStatus | null>(null)
const apiKeyHint = ref('')
const sandboxApiKeyHint = ref('')
const panelPasswordHint = ref('')
const panelPasswordInput = ref('')
const loggingIn = ref(false)
const verifying2fa = ref(false)
const loginMessage = ref('')
const loginOk = ref(false)
const pending2faToken = ref('')
const twoFaCode = ref('')
const iranpayamakBaseUrl = 'https://api.iranpayamak.com'

const providerForm = ref<SmsProviderSettings & { api_key: string; sandbox_api_key: string }>({
  provider_mode: 'mock',
  api_key: '',
  sandbox_api_key: '',
  base_url: 'https://api.sms.ir/v1',
  is_sandbox: false,
  is_active: true,
  line_number: '',
  number_format: 'english',
  panel_username: '',
  last_test_at: null,
  last_test_status: 'unknown',
  last_test_message: '',
})

const otpForm = ref<OtpSettings>({
  otp_length: 6,
  expiry_seconds: 120,
  max_verify_attempts: 5,
  verify_window_seconds: 900,
  rate_limit_count: 5,
  rate_limit_window_seconds: 900,
  resend_delay_seconds: 60,
  ip_rate_limit_count: 20,
  ip_rate_limit_window_seconds: 3600,
})

const authForm = ref<AuthSettings>({
  otp_login_enabled: true,
  access_token_lifetime_minutes: 15,
  refresh_token_lifetime_days: 7,
  rotate_refresh_tokens: true,
  admin_bypass_phone: '',
})

const templates = ref<OtpTemplate[]>([])
const templateDialog = ref<HTMLDialogElement | null>(null)
const editingTemplate = ref<OtpTemplate | null>(null)
const templateForm = ref({
  name: 'ورود ادمین',
  sms_ir_template_id: 394212 as number | undefined,
  pattern_code: '',
  parameter_name: 'CODE',
  body_preview: 'کد تایید ورود شما: {CODE}',
})

const savingProvider = ref(false)
const savingOtp = ref(false)
const savingAuth = ref(false)
const savingTemplate = ref(false)
const testing = ref(false)
const testMessage = ref('')
const testOk = ref(false)
const loadError = ref('')

const templatePreview = computed(() => {
  const body = templateForm.value.body_preview || ''
  const param = templateForm.value.parameter_name || 'Code'
  return body.replace(`{${param}}`, '123456').replace('{Code}', '123456').replace('{CODE}', '123456')
})

const isIranPayamak = computed(() =>
  (providerForm.value.provider_mode || status.value?.provider_mode) === 'iranpayamak',
)
const isSmsIr = computed(() =>
  (providerForm.value.provider_mode || status.value?.provider_mode) === 'smsir',
)
const providerLabel = computed(() => {
  const m = providerForm.value.provider_mode
  if (m === 'iranpayamak') return 'IranPayamak'
  if (m === 'smsir') return 'SMS.ir'
  return 'Mock'
})
const runtimeLabel = computed(() => {
  const r = status.value?.runtime_provider
  if (r === 'iranpayamak') return 'IranPayamak'
  if (r === 'smsir') return 'SMS.ir'
  return 'Mock'
})
const runtimeBadgeClass = computed(() => {
  const r = status.value?.runtime_provider
  return r === 'mock' ? 'badge-ghost' : 'badge-success'
})

function onProviderModeChange() {
  if (providerForm.value.provider_mode === 'iranpayamak') {
    providerForm.value.base_url = iranpayamakBaseUrl
    providerForm.value.is_sandbox = false
  } else if (providerForm.value.provider_mode === 'smsir') {
    providerForm.value.base_url = 'https://api.sms.ir/v1'
  }
}

function buildProviderPayload() {
  const { api_key, sandbox_api_key, ...settings } = providerForm.value
  const body: Record<string, unknown> = { ...settings }
  const newKey = api_key?.trim()
  const newSandboxKey = sandbox_api_key?.trim()
  if (newKey) body.api_key = newKey
  if (newSandboxKey && isSmsIr.value) body.sandbox_api_key = newSandboxKey
  const pwd = panelPasswordInput.value?.trim()
  if (pwd) body.panel_password = pwd
  return body
}

function applyProviderResponse(provider: SmsProviderSettings & { api_key?: string; sandbox_api_key?: string; panel_password?: string }) {
  providerForm.value = {
    ...provider,
    api_key: '',
    sandbox_api_key: '',
    line_number: provider.line_number || '',
    number_format: provider.number_format || 'english',
    panel_username: provider.panel_username || '',
    base_url: provider.base_url || (provider.provider_mode === 'iranpayamak' ? iranpayamakBaseUrl : 'https://api.sms.ir/v1'),
  }
  apiKeyHint.value = provider.api_key || apiKeyHint.value
  sandboxApiKeyHint.value = provider.sandbox_api_key || sandboxApiKeyHint.value
  panelPasswordHint.value = provider.panel_password || panelPasswordHint.value
  panelPasswordInput.value = ''
}

async function loadAll() {
  loading.value = true
  loadError.value = ''
  try {
    const [provider, otp, auth, tpls, st] = await Promise.all([
      apiFetch<SmsProviderSettings>('/admin/sms/provider/'),
      apiFetch<OtpSettings>('/admin/otp/settings/'),
      apiFetch<AuthSettings>('/admin/auth/settings/'),
      apiFetch<OtpTemplate[] | { results: OtpTemplate[] }>('/admin/sms/templates/'),
      apiFetch<SmsProviderStatus>('/admin/sms/provider/status/'),
    ])
    providerForm.value = {
      ...provider,
      api_key: '',
      sandbox_api_key: '',
      base_url: provider.base_url || 'https://api.sms.ir/v1',
    }
    apiKeyHint.value = provider.api_key || ''
    sandboxApiKeyHint.value = provider.sandbox_api_key || ''
    otpForm.value = otp
    authForm.value = auth
    templates.value = Array.isArray(tpls) ? tpls : (tpls.results ?? [])
    status.value = st
  } catch (e: unknown) {
    loadError.value = extractApiError(e, 'خطا در بارگذاری تنظیمات SMS')
  } finally {
    loading.value = false
  }
}

async function saveProvider() {
  savingProvider.value = true
  testMessage.value = ''
  try {
    const provider = await apiFetch<SmsProviderSettings & { api_key?: string; sandbox_api_key?: string }>('/admin/sms/provider/', {
      method: 'PATCH',
      body: buildProviderPayload(),
    })
    applyProviderResponse(provider)
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
    if (activeTab.value === 'templates') {
      await reloadTemplates()
    }
  } catch (e: unknown) {
    testOk.value = false
    testMessage.value = extractApiError(e, 'خطا در ذخیره تنظیمات')
  } finally { savingProvider.value = false }
}

async function testConnection() {
  testing.value = true
  testMessage.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string }>('/admin/sms/provider/test/', {
      method: 'POST',
      body: buildProviderPayload(),
    })
    testOk.value = res.success
    testMessage.value = res.message
    const provider = await apiFetch<SmsProviderSettings & { api_key?: string; sandbox_api_key?: string }>('/admin/sms/provider/')
    applyProviderResponse(provider)
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  } catch (e: unknown) {
    testOk.value = false
    testMessage.value = extractApiError(e, 'خطا در تست اتصال')
  } finally { testing.value = false }
}

async function saveOtp() {
  savingOtp.value = true
  try {
    otpForm.value = await apiFetch<OtpSettings>('/admin/otp/settings/', { method: 'PATCH', body: otpForm.value })
  } finally { savingOtp.value = false }
}

async function saveAuth() {
  savingAuth.value = true
  try {
    authForm.value = await apiFetch<AuthSettings>('/admin/auth/settings/', { method: 'PATCH', body: authForm.value })
  } finally { savingAuth.value = false }
}

async function panelLogin() {
  loggingIn.value = true
  loginMessage.value = ''
  pending2faToken.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string; requires_2fa?: boolean; token?: string }>(
      '/admin/sms/provider/login/',
      {
        method: 'POST',
        body: {
          username: providerForm.value.panel_username,
          password: panelPasswordInput.value || undefined,
        },
      },
    )
    loginOk.value = res.success && !res.requires_2fa
    loginMessage.value = res.message
    if (res.requires_2fa && res.token) {
      pending2faToken.value = res.token
      loginOk.value = false
    } else {
      status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
    }
  } catch (e: unknown) {
    loginOk.value = false
    loginMessage.value = extractApiError(e, 'خطا در ورود')
  } finally { loggingIn.value = false }
}

async function verify2fa() {
  verifying2fa.value = true
  try {
    const res = await apiFetch<{ success: boolean; message: string }>('/admin/sms/provider/verify-2fa/', {
      method: 'POST',
      body: { token: pending2faToken.value, code: twoFaCode.value },
    })
    loginOk.value = res.success
    loginMessage.value = res.message
    pending2faToken.value = ''
    twoFaCode.value = ''
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  } catch (e: unknown) {
    loginOk.value = false
    loginMessage.value = extractApiError(e, 'خطا در تأیید 2FA')
  } finally { verifying2fa.value = false }
}

function openTemplateForm(tpl?: OtpTemplate) {
  editingTemplate.value = tpl || null
  if (tpl) {
    templateForm.value = {
      name: tpl.name,
      sms_ir_template_id: tpl.sms_ir_template_id ?? undefined,
      pattern_code: tpl.pattern_code || '',
      parameter_name: tpl.parameter_name,
      body_preview: tpl.body_preview,
    }
  } else {
    templateForm.value = {
      name: 'ورود ادمین',
      sms_ir_template_id: isIranPayamak.value ? undefined : 394212,
      pattern_code: '',
      parameter_name: 'CODE',
      body_preview: 'کد تایید ورود شما: {CODE}',
    }
  }
  templateDialog.value?.showModal()
}

function closeTemplateForm() {
  templateDialog.value?.close()
}

async function reloadTemplates() {
  const res = await apiFetch<OtpTemplate[] | { results: OtpTemplate[] }>('/admin/sms/templates/')
  templates.value = Array.isArray(res) ? res : (res.results ?? [])
}

async function saveTemplate() {
  savingTemplate.value = true
  try {
    const body: Record<string, unknown> = { ...templateForm.value }
    if (isIranPayamak.value) {
      delete body.sms_ir_template_id
    } else {
      delete body.pattern_code
    }
    if (editingTemplate.value?.id) {
      await apiFetch(`/admin/sms/templates/${editingTemplate.value.id}/`, {
        method: 'PATCH',
        body,
      })
    } else {
      await apiFetch('/admin/sms/templates/', { method: 'POST', body })
    }
    await reloadTemplates()
    closeTemplateForm()
  } finally { savingTemplate.value = false }
}

async function toggleTemplate(tpl: OtpTemplate) {
  if (tpl.is_active) {
    await apiFetch(`/admin/sms/templates/${tpl.id}/`, { method: 'PATCH', body: { is_active: false } })
  } else {
    await apiFetch(`/admin/sms/templates/${tpl.id}/activate/`, { method: 'POST' })
  }
  await reloadTemplates()
}

async function setDefault(tpl: OtpTemplate) {
  await apiFetch(`/admin/sms/templates/${tpl.id}/set-default/`, { method: 'POST' })
  await reloadTemplates()
}

onMounted(loadAll)
</script>
