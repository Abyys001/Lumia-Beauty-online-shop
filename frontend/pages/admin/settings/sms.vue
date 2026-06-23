<template>
  <div class="max-w-4xl space-y-4">
    <NuxtLink to="/admin/settings" class="text-sm text-lumia-gold hover:underline inline-block">
      ← بازگشت به تنظیمات
    </NuxtLink>

    <div v-if="loadError" class="alert alert-error text-sm">{{ loadError }}</div>
    <div
      v-if="status?.runtime_provider === 'mock' || status?.is_sandbox"
      class="alert alert-warning text-sm"
    >
      <span v-if="status?.runtime_provider === 'mock'">حالت Mock فعال است — پیامک واقعی ارسال نمی‌شود.</span>
      <span v-else-if="status?.is_sandbox">حالت Sandbox SMS.ir فعال است.</span>
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
        <h2 class="font-bold text-lumia-dark">تنظیمات SMS.ir</h2>
        <div class="flex items-center gap-2 text-xs">
          <span class="badge" :class="status?.runtime_provider === 'smsir' ? 'badge-success' : 'badge-ghost'">
            {{ status?.runtime_provider === 'smsir' ? 'SMS.ir' : 'Mock' }}
          </span>
          <span v-if="status?.is_sandbox" class="badge badge-warning">Sandbox</span>
        </div>
      </div>

      <div class="grid sm:grid-cols-2 gap-4">
        <div>
          <label class="label-text text-xs block mb-1">ارائه‌دهنده</label>
          <select v-model="providerForm.provider_mode" class="select select-bordered w-full">
            <option value="mock">Mock (توسعه)</option>
            <option value="smsir">SMS.ir</option>
          </select>
        </div>
        <div class="flex items-end gap-4">
          <label class="label cursor-pointer gap-2">
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
        <label class="label-text text-xs block mb-1">API Key</label>
        <input v-model="providerForm.api_key" type="password" class="input input-bordered w-full" dir="ltr" autocomplete="off" placeholder="کلید API" />
      </div>
      <div>
        <label class="label-text text-xs block mb-1">Base URL</label>
        <input v-model="providerForm.base_url" type="url" class="input input-bordered w-full" dir="ltr" />
      </div>

      <div v-if="status" class="rounded-xl bg-base-200/40 p-4 text-sm space-y-1">
        <div>اعتبار: {{ status.credit ?? '—' }}</div>
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
        <div class="overflow-x-auto">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-xs text-lumia-dark/60">
                <th>نام</th>
                <th>Template ID</th>
                <th>پارامتر</th>
                <th>پیش‌فرض</th>
                <th>فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tpl in templates" :key="tpl.id">
                <td>{{ tpl.name }}</td>
                <td dir="ltr">{{ tpl.sms_ir_template_id }}</td>
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
            <input v-model.number="templateForm.sms_ir_template_id" type="number" class="input input-bordered w-full" dir="ltr" placeholder="Template ID" required />
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

const { apiFetch } = useApi()

const tabs = [
  { id: 'provider', label: 'SMS.ir' },
  { id: 'templates', label: 'قالب OTP' },
  { id: 'otp', label: 'OTP' },
  { id: 'auth', label: 'احراز هویت' },
] as const

type TabId = typeof tabs[number]['id']

const activeTab = ref<TabId>('provider')
const loading = ref(true)
const status = ref<SmsProviderStatus | null>(null)

const providerForm = ref<SmsProviderSettings & { api_key: string }>({
  provider_mode: 'mock',
  api_key: '',
  base_url: 'https://api.sms.ir/v1',
  is_sandbox: true,
  is_active: true,
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
  name: '',
  sms_ir_template_id: 123456,
  parameter_name: 'CODE',
  body_preview: 'کد تایید شما: {CODE}',
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
    providerForm.value = { ...provider, api_key: provider.api_key || '' }
    otpForm.value = otp
    authForm.value = auth
    templates.value = Array.isArray(tpls) ? tpls : (tpls.results ?? [])
    status.value = st
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    loadError.value = err.data?.detail || 'خطا در بارگذاری تنظیمات SMS'
  } finally {
    loading.value = false
  }
}

async function saveProvider() {
  savingProvider.value = true
  try {
    await apiFetch('/admin/sms/provider/', { method: 'PATCH', body: providerForm.value })
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  } finally { savingProvider.value = false }
}

async function testConnection() {
  testing.value = true
  testMessage.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string }>('/admin/sms/provider/test/', { method: 'POST' })
    testOk.value = res.success
    testMessage.value = res.message
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  } catch (e: unknown) {
    testOk.value = false
    const err = e as { data?: { message?: string } }
    testMessage.value = err.data?.message || 'خطا در تست اتصال'
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

function openTemplateForm(tpl?: OtpTemplate) {
  editingTemplate.value = tpl || null
  if (tpl) {
    templateForm.value = {
      name: tpl.name,
      sms_ir_template_id: tpl.sms_ir_template_id,
      parameter_name: tpl.parameter_name,
      body_preview: tpl.body_preview,
    }
  } else {
    templateForm.value = {
      name: '',
      sms_ir_template_id: 123456,
      parameter_name: 'CODE',
      body_preview: 'کد تایید شما: {CODE}',
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
    if (editingTemplate.value?.id) {
      await apiFetch(`/admin/sms/templates/${editingTemplate.value.id}/`, {
        method: 'PATCH',
        body: templateForm.value,
      })
    } else {
      await apiFetch('/admin/sms/templates/', { method: 'POST', body: templateForm.value })
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
