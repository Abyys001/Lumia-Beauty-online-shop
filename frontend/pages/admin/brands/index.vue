<template>
  <div class="min-w-0 max-w-full">
    <div class="flex justify-end mb-5">
      <button class="btn btn-primary btn-sm gap-2" @click="openModal()">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        برند جدید
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden min-w-0">
      <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

      <template v-else>
        <div class="lg:hidden divide-y divide-base-200">
          <div v-for="brand in brands" :key="brand.id" class="px-4 py-3 flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg overflow-hidden bg-base-200 flex items-center justify-center shrink-0">
              <img v-if="brand.logo" :src="brand.logo" class="w-full h-full object-contain p-1" />
              <span v-else class="text-lumia-dark/20 text-xs">B</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm truncate">{{ brand.name }}</div>
              <div class="text-xs text-lumia-dark/40 truncate" dir="ltr">{{ brand.slug }}</div>
            </div>
            <input type="checkbox" class="toggle toggle-success toggle-sm shrink-0" :checked="brand.is_active" @change="toggleActive(brand, $event)" />
            <button class="btn btn-ghost btn-xs text-lumia-gold shrink-0" @click="openModal(brand)">ویرایش</button>
          </div>
        </div>

        <div class="hidden lg:block admin-table-wrap">
          <table class="table w-full">
          <thead class="bg-base-200/50">
            <tr class="text-lumia-dark/60 text-xs">
              <th class="font-medium text-right">لوگو</th>
              <th class="font-medium text-right">نام</th>
              <th class="font-medium text-right">فعال</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="brand in brands" :key="brand.id" class="hover:bg-base-200/30">
              <td>
                <div class="w-10 h-10 rounded-lg overflow-hidden bg-base-200 flex items-center justify-center">
                  <img v-if="brand.logo" :src="brand.logo" class="w-full h-full object-contain p-1" />
                  <span v-else class="text-lumia-dark/20 text-xs">B</span>
                </div>
              </td>
              <td>
                <div class="font-medium text-sm">{{ brand.name }}</div>
                <div class="text-xs text-lumia-dark/40" dir="ltr">{{ brand.slug }}</div>
              </td>
              <td>
                <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="brand.is_active" @change="toggleActive(brand, $event)" />
              </td>
              <td>
                <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openModal(brand)">ویرایش</button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </template>
    </div>

    <!-- Modal -->
    <dialog ref="modalEl" class="modal">
      <div class="modal-box max-w-md">
        <h3 class="font-bold text-lumia-dark mb-4">{{ editing?.id ? 'ویرایش برند' : 'برند جدید' }}</h3>
        <form @submit.prevent="save" class="space-y-3">
          <div>
            <label class="label-text text-xs block mb-1">نام *</label>
            <input v-model="form.name" type="text" class="input input-bordered w-full input-sm" required />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">اسلاگ</label>
            <input v-model="form.slug" type="text" class="input input-bordered w-full input-sm" dir="ltr" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">لوگو</label>
            <AdminImageUpload label="آپلود لوگو" v-model="logoFile" />
            <img v-if="editing?.logo && !logoFile" :src="editing.logo" class="w-16 h-16 object-contain mt-2 rounded border border-base-200" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">فعال</span>
          </label>
          <div class="modal-action gap-2 mt-4">
            <button type="button" class="btn btn-ghost btn-sm" @click="closeModal">لغو</button>
            <button v-if="editing?.id" type="button" class="btn btn-error btn-outline btn-sm" @click="deleteBrand">حذف</button>
            <button type="submit" class="btn btn-primary btn-sm">ذخیره</button>
          </div>
        </form>
      </div>
      <form method="dialog" class="modal-backdrop"><button @click="closeModal">بستن</button></form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const brands = ref<any[]>([])
const loading = ref(true)
const modalEl = ref<HTMLDialogElement | null>(null)
const editing = ref<any>(null)
const logoFile = ref<File | null>(null)
const form = ref({ name: '', slug: '', is_active: true })

async function load() {
  loading.value = true
  const res = await apiFetch<any>('/admin/brands/')
  brands.value = res.results ?? res
  loading.value = false
}

function openModal(brand?: any) {
  editing.value = brand ?? null
  logoFile.value = null
  form.value = brand ? { name: brand.name, slug: brand.slug, is_active: brand.is_active } : { name: '', slug: '', is_active: true }
  modalEl.value?.showModal()
}

function closeModal() { modalEl.value?.close() }

async function save() {
  let body: FormData | Record<string, any>
  if (logoFile.value) {
    const fd = new FormData()
    fd.append('name', form.value.name)
    fd.append('slug', form.value.slug)
    fd.append('is_active', String(form.value.is_active))
    fd.append('logo', logoFile.value)
    body = fd
  } else {
    body = { ...form.value }
  }

  if (editing.value?.id) {
    const updated = await apiFetch<any>(`/admin/brands/${editing.value.id}/`, { method: 'PATCH', body })
    const idx = brands.value.findIndex(b => b.id === editing.value.id)
    if (idx !== -1) brands.value[idx] = updated
  } else {
    const created = await apiFetch<any>('/admin/brands/', { method: 'POST', body })
    brands.value.push(created)
  }
  closeModal()
}

async function deleteBrand() {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/brands/${editing.value.id}/`, { method: 'DELETE' })
  brands.value = brands.value.filter(b => b.id !== editing.value.id)
  closeModal()
}

async function toggleActive(brand: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/brands/${brand.id}/`, { method: 'PATCH', body: { is_active: val } })
  brand.is_active = val
}

onMounted(load)
</script>
