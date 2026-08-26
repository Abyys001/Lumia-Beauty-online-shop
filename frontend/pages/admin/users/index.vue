<template>
  <div>
    <!-- Toolbar -->
    <div class="flex flex-wrap items-center gap-2 mb-5">
      <input
        v-model="search"
        type="text"
        placeholder="جستجو شماره تلفن / نام..."
        class="input input-bordered input-sm flex-1 min-w-[12rem]"
        @input="debouncedFetch"
      />
      <select v-model="roleFilter" class="select select-bordered select-sm" @change="reload">
        <option value="">همه‌ی نقش‌ها</option>
        <option value="staff">ادمین‌ها</option>
        <option value="customer">مشتری‌ها</option>
      </select>
      <select v-model="activeFilter" class="select select-bordered select-sm" @change="reload">
        <option value="">فعال و غیرفعال</option>
        <option value="true">فقط فعال</option>
        <option value="false">فقط غیرفعال</option>
      </select>
      <button class="btn btn-primary btn-sm" @click="openCreate">کاربر جدید</button>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">
      در حال بارگذاری...
    </div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div v-for="user in users" :key="user.id" class="bg-white rounded-xl p-3 border border-base-200">
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="font-mono text-sm font-medium">{{ user.phone }}</span>
                <AdminRoleBadge :user="user" />
              </div>
              <div class="text-sm text-lumia-dark/70 mt-0.5">{{ user.first_name }} {{ user.last_name }}</div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/40 flex-wrap">
                <span v-if="user.email">{{ user.email }}</span>
                <span>{{ formatDate(user.date_joined) }}</span>
                <span>{{ user.address_count }} آدرس</span>
                <span v-if="user.device_count">{{ user.device_count }} دستگاه</span>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <input
                type="checkbox"
                class="toggle toggle-success toggle-sm"
                :checked="user.is_active"
                @change="toggleActive(user, $event)"
              />
              <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openDetail(user)">مدیریت</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">شماره تلفن</th>
                <th class="font-medium text-right">نام</th>
                <th class="font-medium text-right">نقش</th>
                <th class="font-medium text-right">ایمیل</th>
                <th class="font-medium text-right">دستگاه‌ها</th>
                <th class="font-medium text-right">آخرین ورود</th>
                <th class="font-medium text-right">فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="hover:bg-base-200/30 transition-colors">
                <td class="font-mono text-sm">{{ user.phone }}</td>
                <td class="text-sm">{{ user.first_name }} {{ user.last_name }}</td>
                <td><AdminRoleBadge :user="user" /></td>
                <td class="text-sm text-lumia-dark/60">{{ user.email || '—' }}</td>
                <td class="text-sm text-lumia-dark/60">{{ user.device_count }}</td>
                <td class="text-sm text-lumia-dark/50">{{ user.last_login ? formatDate(user.last_login) : '—' }}</td>
                <td>
                  <input
                    type="checkbox"
                    class="toggle toggle-success toggle-sm"
                    :checked="user.is_active"
                    @change="toggleActive(user, $event)"
                  />
                </td>
                <td><button class="btn btn-ghost btn-xs text-lumia-gold" @click="openDetail(user)">مدیریت</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="totalCount > 0" class="mt-3 px-2 py-3 flex items-center justify-between">
        <span class="text-sm text-lumia-dark/50">{{ totalCount }} کاربر</span>
        <div class="flex gap-2">
          <button class="btn btn-ghost btn-sm" :disabled="!prevPage" @click="goToPage(currentPage - 1)">قبلی</button>
          <span class="btn btn-ghost btn-sm pointer-events-none">{{ currentPage }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="!nextPage" @click="goToPage(currentPage + 1)">بعدی</button>
        </div>
      </div>
    </template>

    <!-- Manage modal -->
    <dialog ref="detailEl" class="modal">
      <div v-if="selected" class="modal-box max-w-2xl w-full mx-4">
        <div class="flex items-start justify-between gap-3 mb-4">
          <div>
            <h3 class="font-bold text-lumia-dark">{{ selected.first_name }} {{ selected.last_name }}</h3>
            <p class="font-mono text-sm text-lumia-dark/50">{{ selected.phone }}</p>
          </div>
          <AdminRoleBadge :user="selected" />
        </div>

        <div v-if="modalError" class="alert alert-error text-sm py-2 rounded-xl mb-3">{{ modalError }}</div>
        <div v-if="modalSuccess" class="alert alert-success text-sm py-2 rounded-xl mb-3">{{ modalSuccess }}</div>

        <div role="tablist" class="tabs tabs-boxed mb-4">
          <button
            v-for="t in TABS"
            :key="t.id"
            role="tab"
            class="tab"
            :class="{ 'tab-active': modalTab === t.id }"
            @click="switchTab(t.id)"
          >
            {{ t.label }}
          </button>
        </div>

        <!-- Profile -->
        <div v-if="modalTab === 'profile'" class="space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label class="form-control">
              <span class="label-text text-xs mb-1">شماره موبایل</span>
              <input v-model="profileForm.phone" class="input input-bordered input-sm font-mono" dir="ltr" />
            </label>
            <label class="form-control">
              <span class="label-text text-xs mb-1">ایمیل</span>
              <input v-model="profileForm.email" class="input input-bordered input-sm" dir="ltr" />
            </label>
            <label class="form-control">
              <span class="label-text text-xs mb-1">نام</span>
              <input v-model="profileForm.first_name" class="input input-bordered input-sm" />
            </label>
            <label class="form-control">
              <span class="label-text text-xs mb-1">نام خانوادگی</span>
              <input v-model="profileForm.last_name" class="input input-bordered input-sm" />
            </label>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="profileForm.is_active" type="checkbox" class="toggle toggle-success toggle-sm" />
            <span class="text-sm">حساب فعال است</span>
          </label>
          <div class="text-xs text-lumia-dark/50 flex flex-wrap gap-x-4 gap-y-1 border-t pt-3">
            <span>عضویت: {{ formatDate(selected.date_joined) }}</span>
            <span>آخرین ورود: {{ selected.last_login ? formatDate(selected.last_login) : 'هرگز' }}</span>
            <span>{{ selected.order_count }} سفارش</span>
            <span>{{ selected.address_count }} آدرس</span>
          </div>
          <button class="btn btn-primary btn-sm" :disabled="busy" @click="saveProfile">ذخیره</button>

          <div v-if="selected.addresses?.length" class="border-t pt-3">
            <div class="font-medium mb-2 text-lumia-dark/60 text-xs">آدرس‌ها</div>
            <div v-for="addr in selected.addresses" :key="addr.id" class="bg-base-200/50 rounded-lg p-3 mb-2">
              <div class="font-medium text-sm">{{ addr.title }}</div>
              <div class="text-lumia-dark/60 text-xs">{{ addr.province }}، {{ addr.city }}، {{ addr.address_line }}</div>
            </div>
          </div>
        </div>

        <!-- Password -->
        <div v-else-if="modalTab === 'password'" class="space-y-3">
          <p class="text-xs text-lumia-dark/60 leading-relaxed">
            رمز جدید را وارد کنید و آن را به کاربر بگویید. رمز فعلی لازم نیست.
          </p>
          <label class="form-control">
            <span class="label-text text-xs mb-1">رمز عبور جدید</span>
            <input
              v-model="passwordForm.password"
              type="text"
              class="input input-bordered input-sm font-mono"
              dir="ltr"
              placeholder="حداقل ۴ کاراکتر"
            />
          </label>
          <div class="flex flex-wrap items-center gap-2">
            <button class="btn btn-ghost btn-xs" @click="passwordForm.password = randomPassword()">
              ساخت رمز تصادفی
            </button>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="passwordForm.revoke_sessions" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">خروج از همه‌ی دستگاه‌ها پس از تغییر رمز</span>
          </label>
          <button class="btn btn-primary btn-sm" :disabled="busy || !passwordForm.password" @click="setPassword">
            تغییر رمز عبور
          </button>
        </div>

        <!-- Roles -->
        <div v-else-if="modalTab === 'roles'" class="space-y-3">
          <div v-if="!isSuperuser" class="alert alert-warning text-sm py-2 rounded-xl">
            فقط مدیر ارشد می‌تواند سطح دسترسی را تغییر دهد.
          </div>
          <template v-else>
            <label class="flex items-start gap-3 cursor-pointer rounded-xl border border-base-200 p-3">
              <input v-model="roleForm.is_staff" type="checkbox" class="checkbox checkbox-sm mt-0.5" />
              <span>
                <span class="block text-sm font-medium">ادمین (دسترسی به پنل مدیریت)</span>
                <span class="block text-xs text-lumia-dark/50 mt-0.5">
                  می‌تواند محصولات، سفارش‌ها و مشتری‌ها را مدیریت کند.
                </span>
              </span>
            </label>
            <label class="flex items-start gap-3 cursor-pointer rounded-xl border border-base-200 p-3">
              <input v-model="roleForm.is_superuser" type="checkbox" class="checkbox checkbox-sm mt-0.5" />
              <span>
                <span class="block text-sm font-medium">مدیر ارشد</span>
                <span class="block text-xs text-lumia-dark/50 mt-0.5">
                  می‌تواند ادمین بسازد یا حذف کند و به حساب ادمین‌های دیگر دسترسی دارد.
                </span>
              </span>
            </label>
            <div v-if="selected.is_protected_phone" class="alert alert-info text-xs py-2 rounded-xl">
              این شماره در فهرست شماره‌های ادمین است و در هر ورود دوباره ادمین می‌شود.
            </div>
            <button class="btn btn-primary btn-sm" :disabled="busy" @click="saveRoles">ذخیره سطح دسترسی</button>
          </template>
        </div>

        <!-- Devices & sessions -->
        <div v-else class="space-y-3">
          <p class="text-xs text-lumia-dark/60 leading-relaxed">
            دستگاه‌هایی که کاربر «مرا به خاطر بسپار» را روی آن‌ها زده و بدون رمز وارد می‌شود.
          </p>
          <p v-if="!selected.trusted_devices?.length" class="text-sm text-lumia-dark/50">
            هیچ دستگاهی به خاطر سپرده نشده است.
          </p>
          <ul v-else class="space-y-2">
            <li
              v-for="device in selected.trusted_devices"
              :key="device.id"
              class="flex items-center justify-between gap-3 rounded-xl border border-base-200 bg-base-200/30 p-3"
            >
              <div class="min-w-0">
                <p class="text-sm font-medium truncate">{{ device.name }}</p>
                <p class="text-xs text-lumia-dark/50 mt-0.5">
                  آخرین استفاده: {{ formatDate(device.last_used_at) }}
                  <span v-if="device.ip_address"> · {{ device.ip_address }}</span>
                </p>
              </div>
              <button class="btn btn-ghost btn-xs text-error flex-shrink-0" :disabled="busy" @click="revokeDevice(device)">
                حذف
              </button>
            </li>
          </ul>
          <div class="border-t pt-3 flex flex-wrap gap-2">
            <button class="btn btn-outline btn-sm" :disabled="busy" @click="revokeSessions">
              خروج از همه‌ی دستگاه‌ها
            </button>
            <button
              v-if="isSuperuser"
              class="btn btn-error btn-outline btn-sm"
              :disabled="busy"
              @click="removeUser"
            >
              {{ confirmingDelete ? 'مطمئنید؟ برای حذف دوباره بزنید' : 'حذف کاربر' }}
            </button>
          </div>
        </div>

        <div class="modal-action">
          <button class="btn btn-ghost btn-sm" @click="closeDetail">بستن</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop"><button>بستن</button></form>
    </dialog>

    <!-- Create modal -->
    <dialog ref="createEl" class="modal">
      <div class="modal-box max-w-lg w-full mx-4">
        <h3 class="font-bold text-lumia-dark mb-4">کاربر جدید</h3>
        <div v-if="createError" class="alert alert-error text-sm py-2 rounded-xl mb-3">{{ createError }}</div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label class="form-control">
            <span class="label-text text-xs mb-1">شماره موبایل *</span>
            <input v-model="createForm.phone" class="input input-bordered input-sm font-mono" dir="ltr" placeholder="09123456789" />
          </label>
          <label class="form-control">
            <span class="label-text text-xs mb-1">رمز عبور *</span>
            <input v-model="createForm.password" type="text" class="input input-bordered input-sm font-mono" dir="ltr" />
          </label>
          <label class="form-control">
            <span class="label-text text-xs mb-1">نام</span>
            <input v-model="createForm.first_name" class="input input-bordered input-sm" />
          </label>
          <label class="form-control">
            <span class="label-text text-xs mb-1">نام خانوادگی</span>
            <input v-model="createForm.last_name" class="input input-bordered input-sm" />
          </label>
          <label class="form-control sm:col-span-2">
            <span class="label-text text-xs mb-1">ایمیل</span>
            <input v-model="createForm.email" class="input input-bordered input-sm" dir="ltr" />
          </label>
        </div>
        <label v-if="isSuperuser" class="flex items-center gap-2 cursor-pointer mt-3">
          <input v-model="createForm.is_staff" type="checkbox" class="checkbox checkbox-sm" />
          <span class="text-sm">این کاربر ادمین باشد</span>
        </label>
        <div class="modal-action">
          <button class="btn btn-ghost btn-sm" @click="createEl?.close()">انصراف</button>
          <button class="btn btn-primary btn-sm" :disabled="busy" @click="createUser">ساخت کاربر</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop"><button>بستن</button></form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import type { AdminUser, AdminUserDetail, TrustedDevice } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const TABS = [
  { id: 'profile', label: 'مشخصات' },
  { id: 'password', label: 'رمز عبور' },
  { id: 'roles', label: 'سطح دسترسی' },
  { id: 'devices', label: 'دستگاه‌ها' },
] as const
type ModalTab = (typeof TABS)[number]['id']

const { apiFetch, formatDate, extractApiError } = useApi()
const auth = useAuthStore()
const isSuperuser = computed(() => !!auth.user?.is_superuser)

const search = ref('')
const roleFilter = ref('')
const activeFilter = ref('')
const users = ref<AdminUser[]>([])
const loading = ref(true)
const totalCount = ref(0)
const nextPage = ref<string | null>(null)
const prevPage = ref<string | null>(null)
const currentPage = ref(1)

const detailEl = ref<HTMLDialogElement | null>(null)
const createEl = ref<HTMLDialogElement | null>(null)
const selected = ref<AdminUserDetail | null>(null)
const modalTab = ref<ModalTab>('profile')
const modalError = ref('')
const modalSuccess = ref('')
const busy = ref(false)
const confirmingDelete = ref(false)

const profileForm = reactive({ phone: '', first_name: '', last_name: '', email: '', is_active: true })
const passwordForm = reactive({ password: '', revoke_sessions: true })
const roleForm = reactive({ is_staff: false, is_superuser: false })
const createForm = reactive({
  phone: '', password: '', first_name: '', last_name: '', email: '', is_staff: false,
})
const createError = ref('')

async function fetchUsers() {
  loading.value = true
  try {
    const params: Record<string, string> = { page: String(currentPage.value) }
    if (search.value) params.search = search.value
    if (roleFilter.value) params.role = roleFilter.value
    if (activeFilter.value) params.is_active = activeFilter.value
    const res = await apiFetch<{
      results: AdminUser[]
      count: number
      next: string | null
      previous: string | null
    }>('/admin/users/', { params })
    users.value = res.results
    totalCount.value = res.count
    nextPage.value = res.next
    prevPage.value = res.previous
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) {
  currentPage.value = page
  fetchUsers()
}

function reload() {
  currentPage.value = 1
  fetchUsers()
}

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(reload, 350)
}

/** Every mutation goes through here so one failed call can't leave a stale modal. */
async function run(action: () => Promise<string>, fallback: string) {
  busy.value = true
  modalError.value = ''
  modalSuccess.value = ''
  try {
    modalSuccess.value = await action()
  } catch (e) {
    modalError.value = extractApiError(e, fallback)
  } finally {
    busy.value = false
  }
}

async function loadDetail(id: string) {
  const full = await apiFetch<AdminUserDetail>(`/admin/users/${id}/`)
  selected.value = full
  Object.assign(profileForm, {
    phone: full.phone,
    first_name: full.first_name,
    last_name: full.last_name,
    email: full.email,
    is_active: full.is_active,
  })
  Object.assign(roleForm, { is_staff: full.is_staff, is_superuser: full.is_superuser })
  return full
}

async function openDetail(user: AdminUser) {
  modalTab.value = 'profile'
  modalError.value = ''
  modalSuccess.value = ''
  confirmingDelete.value = false
  passwordForm.password = ''
  await loadDetail(user.id)
  detailEl.value?.showModal()
}

function switchTab(tab: ModalTab) {
  modalTab.value = tab
  modalError.value = ''
  modalSuccess.value = ''
  confirmingDelete.value = false
}

function closeDetail() {
  detailEl.value?.close()
  selected.value = null
}

async function toggleActive(user: AdminUser, e: Event) {
  const input = e.target as HTMLInputElement
  const val = input.checked
  try {
    await apiFetch(`/admin/users/${user.id}/`, { method: 'PATCH', body: { is_active: val } })
    user.is_active = val
  } catch (err) {
    input.checked = user.is_active
    alert(extractApiError(err, 'تغییر وضعیت کاربر انجام نشد.'))
  }
}

function saveProfile() {
  const id = selected.value!.id
  return run(async () => {
    await apiFetch(`/admin/users/${id}/`, { method: 'PATCH', body: { ...profileForm } })
    await loadDetail(id)
    await fetchUsers()
    return 'مشخصات ذخیره شد.'
  }, 'ذخیره‌ی مشخصات انجام نشد.')
}

function setPassword() {
  const id = selected.value!.id
  return run(async () => {
    const res = await apiFetch<{ detail: string }>(`/admin/users/${id}/set-password/`, {
      method: 'POST',
      body: { ...passwordForm },
    })
    await loadDetail(id)
    return res.detail
  }, 'تغییر رمز عبور انجام نشد.')
}

function saveRoles() {
  const id = selected.value!.id
  return run(async () => {
    await apiFetch(`/admin/users/${id}/roles/`, { method: 'POST', body: { ...roleForm } })
    await loadDetail(id)
    await fetchUsers()
    return 'سطح دسترسی به‌روزرسانی شد.'
  }, 'تغییر سطح دسترسی انجام نشد.')
}

function revokeSessions() {
  const id = selected.value!.id
  return run(async () => {
    const res = await apiFetch<{ detail: string }>(`/admin/users/${id}/revoke-sessions/`, {
      method: 'POST',
      body: {},
    })
    await loadDetail(id)
    await fetchUsers()
    return res.detail
  }, 'ابطال نشست‌ها انجام نشد.')
}

function revokeDevice(device: TrustedDevice) {
  const id = selected.value!.id
  return run(async () => {
    await apiFetch(`/admin/users/${id}/devices/${device.id}/`, { method: 'DELETE' })
    await loadDetail(id)
    await fetchUsers()
    return 'دستگاه حذف شد.'
  }, 'حذف دستگاه انجام نشد.')
}

function removeUser() {
  // Two-click confirm rather than a JS dialog — a modal here would freeze the page.
  if (!confirmingDelete.value) {
    confirmingDelete.value = true
    return
  }
  const id = selected.value!.id
  confirmingDelete.value = false
  return run(async () => {
    await apiFetch(`/admin/users/${id}/`, { method: 'DELETE' })
    closeDetail()
    await fetchUsers()
    return 'کاربر حذف شد.'
  }, 'حذف کاربر انجام نشد.')
}

function openCreate() {
  createError.value = ''
  Object.assign(createForm, {
    phone: '', password: '', first_name: '', last_name: '', email: '', is_staff: false,
  })
  createEl.value?.showModal()
}

async function createUser() {
  busy.value = true
  createError.value = ''
  try {
    await apiFetch('/admin/users/', { method: 'POST', body: { ...createForm } })
    createEl.value?.close()
    await fetchUsers()
  } catch (e) {
    createError.value = extractApiError(e, 'ساخت کاربر انجام نشد.')
  } finally {
    busy.value = false
  }
}

const PASSWORD_ALPHABET = 'abcdefghijkmnpqrstuvwxyz23456789'
function randomPassword(): string {
  const bytes = new Uint32Array(10)
  crypto.getRandomValues(bytes)
  return Array.from(bytes, b => PASSWORD_ALPHABET[b % PASSWORD_ALPHABET.length]).join('')
}

onMounted(fetchUsers)
</script>
