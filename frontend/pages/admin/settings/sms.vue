<template>
  <div class="max-w-5xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline inline-block">
      داشبورد SMS →
    </NuxtLink>

    <div v-if="loadError" class="alert alert-error text-sm">{{ loadError }}</div>
    <div
      v-if="status?.runtime_provider === 'mock' || (status?.is_sandbox && isActiveSmsIr)"
      class="alert alert-warning text-sm"
    >
      <div class="space-y-1">
        <p v-if="status?.runtime_provider === 'mock'">
          حالت Mock فعال است — پیامک واقعی ارسال نمی‌شود.
        </p>
        <template v-else-if="status?.is_sandbox">
          <p class="font-semibold">حالت Sandbox فعال است — پیامک واقعی ارسال نمی‌شود.</p>
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

    <!-- Provider cards -->
    <div v-else-if="activeTab === 'provider'" class="space-y-4">
      <div class="flex flex-wrap items-center gap-2 text-sm text-lumia-dark/60">
        <span>ارائه‌دهنده فعال:</span>
        <span class="badge badge-primary">{{ activeProviderLabel }}</span>
      </div>

      <div class="grid lg:grid-cols-3 gap-4">
        <div
          v-for="card in providerCards"
          :key="card.type"
          class="bg-white rounded-2xl border shadow-sm transition-all"
          :class="card.profile?.is_active
            ? 'border-lumia-gold ring-2 ring-lumia-gold/30'
            : 'border-base-200'"
        >
          <!-- Card header -->
          <div class="p-5 space-y-3">
            <div class="flex items-start justify-between gap-2">
              <div>
                <h3 class="font-bold text-lumia-dark">{{ card.label }}</h3>
                <p class="text-xs text-lumia-dark/50 mt-0.5">{{ card.description }}</p>
              </div>
              <span
                class="badge badge-sm shrink-0"
                :class="card.profile?.is_active ? 'badge-primary' : 'badge-ghost'"
              >
                {{ card.profile?.is_active ? 'در حال استفاده' : 'غیرفعال' }}
              </span>
            </div>

            <div class="text-xs space-y-1 text-lumia-dark/60">
              <div v-if="card.type !== 'mock'">
                کلید:
                <span dir="ltr" class="font-mono">{{ card.profile?.api_key || '—' }}</span>
              </div>
              <div>
                آخرین تست:
                {{ card.profile?.last_test_status || '—' }}
                <span v-if="card.profile?.last_test_message"> — {{ card.profile.last_test_message }}</span>
              </div>
            </div>

            <div class="flex flex-wrap gap-2">
              <button
                v-if="!card.profile?.is_active"
                type="button"
                class="btn btn-primary btn-xs"
                :class="{ loading: activating === card.type }"
                @click="activateProvider(card.type)"
              >
                فعال‌سازی
              </button>
              <button
                type="button"
                class="btn btn-outline btn-xs"
                @click="toggleExpanded(card.type)"
              >
                {{ expandedCard === card.type ? 'بستن ▲' : 'تنظیمات ▼' }}
              </button>
            </div>
          </div>

          <!-- Inline form -->
          <div
            v-if="expandedCard === card.type"
            class="border-t border-base-200 p-5 space-y-4 bg-base-200/20 rounded-b-2xl"
          >
            <template v-if="card.type === 'mock'">
              <p class="text-sm text-lumia-dark/60">
                در حالت Mock پیامک واقعی ارسال نمی‌شود. برای تست OTP از کنسول یا لاگ‌ها استفاده کنید.
              </p>
            </template>

            <template v-else-if="card.type === 'smsir'">
              <label class="label cursor-pointer justify-start gap-2">
                <input
                  v-model="cardForms.smsir.is_sandbox"
                  type="checkbox"
                  class="toggle toggle-warning toggle-sm"
                />
                <span class="label-text text-sm">Sandbox</span>
              </label>
              <div>
                <label class="label-text text-xs block mb-1">کلید Production</label>
                <p v-if="cardForms.smsir.api_key_hint" class="text-xs text-base-content/50 mb-1" dir="ltr">
                  فعلی: {{ cardForms.smsir.api_key_hint }}
                </p>
                <input
                  v-model="cardForms.smsir.api_key"
                  type="password"
                  class="input input-bordered w-full input-sm"
                  dir="ltr"
                  autocomplete="new-password"
                  placeholder="کلید Production"
                />
              </div>
              <div>
                <label class="label-text text-xs block mb-1">کلید Sandbox</label>
                <p v-if="cardForms.smsir.sandbox_api_key_hint" class="text-xs text-base-content/50 mb-1" dir="ltr">
                  فعلی: {{ cardForms.smsir.sandbox_api_key_hint }}
                </p>
                <input
                  v-model="cardForms.smsir.sandbox_api_key"
                  type="password"
                  class="input input-bordered w-full input-sm"
                  dir="ltr"
                  autocomplete="new-password"
                  placeholder="کلید Sandbox (اختیاری)"
                />
              </div>
              <div>
                <label class="label-text text-xs block mb-1">Base URL</label>
                <input
                  :value="cardForms.smsir.base_url || 'https://api.sms.ir/v1'"
                  type="url"
                  class="input input-bordered w-full input-sm"
                  dir="ltr"
                  readonly
                />
              </div>
            </template>

            <template v-else-if="card.type === 'iranpayamak'">
              <div>
                <label class="label-text text-xs block mb-1">Api-Key</label>
                <p v-if="cardForms.iranpayamak.api_key_hint" class="text-xs text-base-content/50 mb-1" dir="ltr">
                  فعلی: {{ cardForms.iranpayamak.api_key_hint }}
                </p>
                <input
                  v-model="cardForms.iranpayamak.api_key"
                  type="password"
                  class="input input-bordered w-full input-sm"
                  dir="ltr"
                  autocomplete="new-password"
                  placeholder="Api-Key IranPayamak"
                />
              </div>
              <div class="grid sm:grid-cols-2 gap-3">
                <div>
                  <label class="label-text text-xs block mb-1">شماره خط</label>
                  <input
                    v-model="cardForms.iranpayamak.line_number"
                    type="text"
                    class="input input-bordered w-full input-sm"
                    dir="ltr"
                    placeholder="50002178584000"
                  />
                </div>
                <div>
                  <label class="label-text text-xs block mb-1">فرمت اعداد</label>
                  <select v-model="cardForms.iranpayamak.number_format" class="select select-bordered w-full select-sm">
                    <option value="english">English</option>
                    <option value="persian">Persian</option>
                  </select>
                </div>
              </div>
              <div class="rounded-xl border border-base-200 p-3 space-y-2">
                <h4 class="font-semibold text-xs">ورود پنل (اختیاری — برای لیست خطوط)</h4>
                <div class="grid sm:grid-cols-2 gap-2">
                  <input
                    v-model="cardForms.iranpayamak.panel_username"
                    type="text"
                    class="input input-bordered w-full input-sm"
                    dir="ltr"
                    placeholder="نام کاربری"
                  />
                  <input
                    v-model="cardForms.iranpayamak.panel_password"
                    type="password"
                    class="input input-bordered w-full input-sm"
                    dir="ltr"
                    autocomplete="new-password"
                    placeholder="رمز عبور"
                  />
                </div>
                <div class="flex flex-wrap gap-2 items-center">
                  <button
                    type="button"
                    class="btn btn-outline btn-xs"
                    :class="{ loading: loggingIn }"
                    @click="panelLogin('iranpayamak')"
                  >
                    ورود
                  </button>
                  <span v-if="card.profile?.has_bearer_token" class="badge badge-success badge-xs">Bearer فعال</span>
                </div>
                <div v-if="loginMessage" class="text-xs" :class="loginOk ? 'text-success' : 'text-warning'">
                  {{ loginMessage }}
                </div>
                <div v-if="pending2faToken" class="grid sm:grid-cols-2 gap-2 pt-2 border-t border-base-200">
                  <input
                    v-model="twoFaCode"
                    type="text"
                    class="input input-bordered w-full input-sm"
                    dir="ltr"
                    placeholder="کد 2FA"
                    maxlength="8"
                  />
                  <button
                    type="button"
                    class="btn btn-outline btn-xs"
                    :class="{ loading: verifying2fa }"
                    @click="verify2fa('iranpayamak')"
                  >
                    تأیید 2FA
                  </button>
                </div>
              </div>
            </template>

            <div v-if="card.type !== 'mock'" class="flex flex-wrap gap-2">
              <button
                type="button"
                class="btn btn-primary btn-sm"
                :class="{ loading: savingCard === card.type }"
                @click="saveCard(card.type)"
              >
                ذخیره
              </button>
              <button
                type="button"
                class="btn btn-outline btn-sm"
                :class="{ loading: testingCard === card.type }"
                @click="testCard(card.type)"
              >
                تست اتصال
              </button>
            </div>
            <div
              v-if="cardMessages[card.type]"
              class="text-sm"
              :class="cardMessagesOk[card.type] ? 'text-success' : 'text-error'"
            >
              {{ cardMessages[card.type] }}
            </div>
          </div>
        </div>
      </div>
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
                <th>{{ isActiveIranPayamak ? 'Pattern' : 'Template ID' }}</th>
                <th>پارامتر</th>
                <th>پیش‌فرض</th>
                <th>فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tpl in templates" :key="tpl.id">
                <td>{{ tpl.name }}</td>
                <td dir="ltr">{{ isActiveIranPayamak ? (tpl.pattern_code || '—') : (tpl.sms_ir_template_id ?? '—') }}</td>
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
              v-if="isActiveIranPayamak"
              v-model="templateForm.pattern_code"
              type="text"
              class="input input-bordered w-full"
              dir="ltr"
              placeholder="Pattern UID"
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
            <input v-model="templateForm.parameter_name" class="input input-bordered w-full" dir="ltr" placeholder="Parameter name" required />
            <textarea v-model="templateForm.body_preview" class="textarea textarea-bordered w-full" rows="3" placeholder="پیش‌نمایش" />
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
  SmsProviderProfile,
  SmsProviderStatus,
} from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, extractApiError } = useApi()

type ProviderType = 'mock' | 'smsir' | 'iranpayamak'

const tabs = [
  { id: 'provider', label: 'ارائه‌دهنده' },
  { id: 'templates', label: 'قالب OTP' },
  { id: 'otp', label: 'OTP' },
  { id: 'auth', label: 'احراز هویت' },
] as const

type TabId = typeof tabs[number]['id']

const activeTab = ref<TabId>('provider')
const loading = ref(true)
const profiles = ref<SmsProviderProfile[]>([])
const status = ref<SmsProviderStatus | null>(null)
const expandedCard = ref<ProviderType | null>(null)
const activating = ref<ProviderType | null>(null)
const savingCard = ref<ProviderType | null>(null)
const testingCard = ref<ProviderType | null>(null)
const cardMessages = ref<Partial<Record<ProviderType, string>>>({})
const cardMessagesOk = ref<Partial<Record<ProviderType, boolean>>>({})

const loggingIn = ref(false)
const verifying2fa = ref(false)
const loginMessage = ref('')
const loginOk = ref(false)
const pending2faToken = ref('')
const twoFaCode = ref('')

const providerCards = computed(() => [
  {
    type: 'mock' as ProviderType,
    label: 'Mock',
    description: 'توسعه — بدون ارسال واقعی',
    profile: profiles.value.find(p => p.provider_type === 'mock'),
  },
  {
    type: 'smsir' as ProviderType,
    label: 'SMS.ir',
    description: 'سرویس پیامک SMS.ir',
    profile: profiles.value.find(p => p.provider_type === 'smsir'),
  },
  {
    type: 'iranpayamak' as ProviderType,
    label: 'IranPayamak',
    description: 'سرویس ایران‌پیامک',
    profile: profiles.value.find(p => p.provider_type === 'iranpayamak'),
  },
])

const cardForms = reactive({
  smsir: {
    api_key: '',
    sandbox_api_key: '',
    api_key_hint: '',
    sandbox_api_key_hint: '',
    is_sandbox: false,
    base_url: 'https://api.sms.ir/v1',
  },
  iranpayamak: {
    api_key: '',
    api_key_hint: '',
    line_number: '',
    number_format: 'english' as 'english' | 'persian',
    panel_username: '',
    panel_password: '',
  },
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

const savingOtp = ref(false)
const savingAuth = ref(false)
const savingTemplate = ref(false)
const loadError = ref('')

const isActiveSmsIr = computed(() => status.value?.runtime_provider === 'smsir')
const isActiveIranPayamak = computed(() => status.value?.runtime_provider === 'iranpayamak')
const activeProviderLabel = computed(() => {
  const activeProfile = profiles.value.find(p => p.is_active)
  const r = activeProfile?.provider_type || status.value?.runtime_provider
  if (r === 'iranpayamak') return 'IranPayamak'
  if (r === 'smsir') return 'SMS.ir'
  return 'Mock'
})

const templatePreview = computed(() => {
  const body = templateForm.value.body_preview || ''
  const param = templateForm.value.parameter_name || 'Code'
  return body.replace(`{${param}}`, '123456').replace('{Code}', '123456').replace('{CODE}', '123456')
})

function syncCardForms() {
  const smsir = profiles.value.find(p => p.provider_type === 'smsir')
  const ip = profiles.value.find(p => p.provider_type === 'iranpayamak')
  if (smsir) {
    cardForms.smsir.is_sandbox = smsir.is_sandbox
    cardForms.smsir.base_url = smsir.base_url || 'https://api.sms.ir/v1'
    cardForms.smsir.api_key_hint = smsir.api_key || ''
    cardForms.smsir.sandbox_api_key_hint = smsir.sandbox_api_key || ''
    cardForms.smsir.api_key = ''
    cardForms.smsir.sandbox_api_key = ''
  }
  if (ip) {
    cardForms.iranpayamak.line_number = ip.line_number || ''
    cardForms.iranpayamak.number_format = ip.number_format || 'english'
    cardForms.iranpayamak.panel_username = ip.panel_username || ''
    cardForms.iranpayamak.api_key_hint = ip.api_key || ''
    cardForms.iranpayamak.api_key = ''
    cardForms.iranpayamak.panel_password = ''
  }
}

function toggleExpanded(type: ProviderType) {
  expandedCard.value = expandedCard.value === type ? null : type
}

function buildCardPayload(type: ProviderType) {
  if (type === 'smsir') {
    const body: Record<string, unknown> = {
      is_sandbox: cardForms.smsir.is_sandbox,
      base_url: cardForms.smsir.base_url,
    }
    if (cardForms.smsir.api_key.trim()) body.api_key = cardForms.smsir.api_key.trim()
    if (cardForms.smsir.sandbox_api_key.trim()) body.sandbox_api_key = cardForms.smsir.sandbox_api_key.trim()
    return body
  }
  if (type === 'iranpayamak') {
    const body: Record<string, unknown> = {
      line_number: cardForms.iranpayamak.line_number,
      number_format: cardForms.iranpayamak.number_format,
      panel_username: cardForms.iranpayamak.panel_username,
    }
    if (cardForms.iranpayamak.api_key.trim()) body.api_key = cardForms.iranpayamak.api_key.trim()
    if (cardForms.iranpayamak.panel_password.trim()) body.panel_password = cardForms.iranpayamak.panel_password.trim()
    return body
  }
  return {}
}

async function loadProfiles() {
  profiles.value = await apiFetch<SmsProviderProfile[]>('/admin/sms/providers/')
  syncCardForms()
}

async function loadAll() {
  loading.value = true
  loadError.value = ''
  try {
    try {
      await loadProfiles()
    } catch (e: unknown) {
      loadError.value = extractApiError(e, 'خطا در بارگذاری پروفایل‌های SMS — migrate را اجرا کنید: docker compose exec backend python manage.py migrate')
      return
    }

    const [otpR, authR, tplR, statusR] = await Promise.allSettled([
      apiFetch<OtpSettings>('/admin/otp/settings/'),
      apiFetch<AuthSettings>('/admin/auth/settings/'),
      apiFetch<OtpTemplate[] | { results: OtpTemplate[] }>('/admin/sms/templates/'),
      apiFetch<SmsProviderStatus>('/admin/sms/provider/status/'),
    ])

    const partialErrors: string[] = []
    if (otpR.status === 'fulfilled') {
      otpForm.value = otpR.value
    } else {
      partialErrors.push('تنظیمات OTP')
    }
    if (authR.status === 'fulfilled') {
      authForm.value = authR.value
    } else {
      partialErrors.push('احراز هویت')
    }
    if (tplR.status === 'fulfilled') {
      const tpls = tplR.value
      templates.value = Array.isArray(tpls) ? tpls : (tpls.results ?? [])
    } else {
      partialErrors.push('قالب‌های OTP')
    }
    if (statusR.status === 'fulfilled') {
      status.value = statusR.value
    } else {
      partialErrors.push('وضعیت ارائه‌دهنده')
    }

    if (partialErrors.length) {
      loadError.value = `برخی بخش‌ها بارگذاری نشدند: ${partialErrors.join('، ')}`
    }
  } catch (e: unknown) {
    loadError.value = extractApiError(e, 'خطا در بارگذاری تنظیمات SMS')
  } finally {
    loading.value = false
  }
}

async function activateProvider(type: ProviderType) {
  activating.value = type
  cardMessages.value[type] = ''
  try {
    await apiFetch(`/admin/sms/providers/${type}/activate/`, { method: 'POST' })
    await loadProfiles()
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
    cardMessagesOk.value[type] = true
    cardMessages.value[type] = 'ارائه‌دهنده فعال شد'
  } catch (e: unknown) {
    cardMessagesOk.value[type] = false
    cardMessages.value[type] = extractApiError(e, 'خطا در فعال‌سازی')
  } finally {
    activating.value = null
  }
}

async function saveCard(type: ProviderType) {
  if (type === 'mock') return
  savingCard.value = type
  cardMessages.value[type] = ''
  try {
    await apiFetch(`/admin/sms/providers/${type}/`, {
      method: 'PATCH',
      body: buildCardPayload(type),
    })
    await loadProfiles()
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
    cardMessagesOk.value[type] = true
    cardMessages.value[type] = 'ذخیره شد'
  } catch (e: unknown) {
    cardMessagesOk.value[type] = false
    cardMessages.value[type] = extractApiError(e, 'خطا در ذخیره')
  } finally {
    savingCard.value = null
  }
}

async function testCard(type: ProviderType) {
  if (type === 'mock') return
  testingCard.value = type
  cardMessages.value[type] = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string }>(`/admin/sms/providers/${type}/test/`, {
      method: 'POST',
      body: buildCardPayload(type),
    })
    cardMessagesOk.value[type] = res.success
    cardMessages.value[type] = res.message
    await loadProfiles()
    status.value = await apiFetch<SmsProviderStatus>('/admin/sms/provider/status/')
  } catch (e: unknown) {
    cardMessagesOk.value[type] = false
    cardMessages.value[type] = extractApiError(e, 'خطا در تست اتصال')
  } finally {
    testingCard.value = null
  }
}

async function panelLogin(type: ProviderType) {
  loggingIn.value = true
  loginMessage.value = ''
  pending2faToken.value = ''
  try {
    const res = await apiFetch<{ success: boolean; message: string; requires_2fa?: boolean; token?: string }>(
      `/admin/sms/providers/${type}/login/`,
      {
        method: 'POST',
        body: {
          username: cardForms.iranpayamak.panel_username,
          password: cardForms.iranpayamak.panel_password || undefined,
        },
      },
    )
    loginOk.value = res.success && !res.requires_2fa
    loginMessage.value = res.message
    if (res.requires_2fa && res.token) {
      pending2faToken.value = res.token
      loginOk.value = false
    } else {
      await loadProfiles()
    }
  } catch (e: unknown) {
    loginOk.value = false
    loginMessage.value = extractApiError(e, 'خطا در ورود')
  } finally {
    loggingIn.value = false
  }
}

async function verify2fa(type: ProviderType) {
  verifying2fa.value = true
  try {
    const res = await apiFetch<{ success: boolean; message: string }>(
      `/admin/sms/providers/${type}/verify-2fa/`,
      { method: 'POST', body: { token: pending2faToken.value, code: twoFaCode.value } },
    )
    loginOk.value = res.success
    loginMessage.value = res.message
    pending2faToken.value = ''
    twoFaCode.value = ''
    await loadProfiles()
  } catch (e: unknown) {
    loginOk.value = false
    loginMessage.value = extractApiError(e, 'خطا در تأیید 2FA')
  } finally {
    verifying2fa.value = false
  }
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
      sms_ir_template_id: tpl.sms_ir_template_id ?? undefined,
      pattern_code: tpl.pattern_code || '',
      parameter_name: tpl.parameter_name,
      body_preview: tpl.body_preview,
    }
  } else {
    templateForm.value = {
      name: 'ورود ادمین',
      sms_ir_template_id: isActiveIranPayamak.value ? undefined : 394212,
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
    const activeType = status.value?.runtime_provider || 'smsir'
    const body: Record<string, unknown> = {
      ...templateForm.value,
      provider_type: activeType,
    }
    if (isActiveIranPayamak.value) {
      delete body.sms_ir_template_id
    } else {
      delete body.pattern_code
    }
    if (editingTemplate.value?.id) {
      await apiFetch(`/admin/sms/templates/${editingTemplate.value.id}/`, { method: 'PATCH', body })
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
