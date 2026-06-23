<template>
  <div>
    <div class="flex flex-wrap gap-3 mb-5">
      <input v-model="search" type="text" placeholder="جستجو شماره تلفن / نام..." class="input input-bordered input-sm flex-1 min-w-0" @input="debouncedFetch" />
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div
          v-for="user in users"
          :key="user.id"
          class="bg-white rounded-xl p-3 border border-base-200"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="font-mono text-sm font-medium">{{ user.phone }}</div>
              <div class="text-sm text-lumia-dark/70 mt-0.5">{{ user.first_name }} {{ user.last_name }}</div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/40 flex-wrap">
                <span v-if="user.email">{{ user.email }}</span>
                <span>{{ formatDate(user.date_joined) }}</span>
                <span>{{ user.address_count }} آدرس</span>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="user.is_active" @change="toggleActive(user, $event)" />
              <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openDetail(user)">جزئیات</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">شماره تلفن</th>
                <th class="font-medium text-right">نام</th>
                <th class="font-medium text-right">ایمیل</th>
                <th class="font-medium text-right">آدرس‌ها</th>
                <th class="font-medium text-right">تاریخ ثبت‌نام</th>
                <th class="font-medium text-right">فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="hover:bg-base-200/30 transition-colors">
                <td class="font-mono text-sm">{{ user.phone }}</td>
                <td class="text-sm">{{ user.first_name }} {{ user.last_name }}</td>
                <td class="text-sm text-lumia-dark/60">{{ user.email || '—' }}</td>
                <td class="text-sm text-lumia-dark/60">{{ user.address_count }}</td>
                <td class="text-sm text-lumia-dark/50">{{ formatDate(user.date_joined) }}</td>
                <td><input type="checkbox" class="toggle toggle-success toggle-sm" :checked="user.is_active" @change="toggleActive(user, $event)" /></td>
                <td><button class="btn btn-ghost btn-xs text-lumia-gold" @click="openDetail(user)">جزئیات</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalCount > 0" class="mt-3 px-2 py-3 flex items-center justify-between">
        <span class="text-sm text-lumia-dark/50">{{ totalCount }} کاربر</span>
        <div class="flex gap-2">
          <button class="btn btn-ghost btn-sm" :disabled="!prevPage" @click="goToPage(currentPage - 1)">قبلی</button>
          <span class="btn btn-ghost btn-sm pointer-events-none">{{ currentPage }}</span>
          <button class="btn btn-ghost btn-sm" :disabled="!nextPage" @click="goToPage(currentPage + 1)">بعدی</button>
        </div>
      </div>
    </template>

    <!-- Detail modal -->
    <dialog ref="detailEl" class="modal">
      <div class="modal-box max-w-lg w-full mx-4" v-if="selectedUser">
        <h3 class="font-bold text-lumia-dark mb-4">{{ selectedUser.phone }}</h3>
        <div class="space-y-3 text-sm">
          <div class="grid grid-cols-2 gap-3">
            <div><span class="text-lumia-dark/50">نام:</span> {{ selectedUser.first_name || '—' }}</div>
            <div><span class="text-lumia-dark/50">نام خانوادگی:</span> {{ selectedUser.last_name || '—' }}</div>
            <div><span class="text-lumia-dark/50">ایمیل:</span> {{ selectedUser.email || '—' }}</div>
            <div><span class="text-lumia-dark/50">تاریخ:</span> {{ formatDate(selectedUser.date_joined) }}</div>
          </div>
          <div v-if="selectedUser.addresses?.length">
            <div class="font-medium mb-2 text-lumia-dark/60 text-xs border-t pt-3">آدرس‌ها</div>
            <div v-for="addr in selectedUser.addresses" :key="addr.id" class="bg-base-200/50 rounded-lg p-3 mb-2">
              <div class="font-medium">{{ addr.title }}</div>
              <div class="text-lumia-dark/60 text-xs">{{ addr.province }}، {{ addr.city }}، {{ addr.address_line }}</div>
            </div>
          </div>
        </div>
        <div class="modal-action">
          <button class="btn btn-ghost btn-sm" @click="detailEl?.close()">بستن</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop"><button>بستن</button></form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatDate } = useApi()

const search = ref('')
const users = ref<any[]>([])
const loading = ref(true)
const totalCount = ref(0)
const nextPage = ref<string | null>(null)
const prevPage = ref<string | null>(null)
const currentPage = ref(1)
const detailEl = ref<HTMLDialogElement | null>(null)
const selectedUser = ref<any>(null)

async function fetchUsers() {
  loading.value = true
  try {
    const params: Record<string, string> = { page: String(currentPage.value) }
    if (search.value) params.search = search.value
    const res = await apiFetch<any>('/admin/users/', { params })
    users.value = res.results
    totalCount.value = res.count
    nextPage.value = res.next
    prevPage.value = res.previous
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) { currentPage.value = page; fetchUsers() }

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { currentPage.value = 1; fetchUsers() }, 350)
}

async function openDetail(user: any) {
  const full = await apiFetch<any>(`/admin/users/${user.id}/`)
  selectedUser.value = full
  detailEl.value?.showModal()
}

async function toggleActive(user: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/users/${user.id}/`, { method: 'PATCH', body: { is_active: val } })
  user.is_active = val
}

onMounted(fetchUsers)
</script>
