<template>
  <div>
    <div class="flex justify-end mb-5">
      <button class="btn btn-primary btn-sm gap-2" @click="openModal()">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        دسته‌بندی جدید
      </button>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <div
          v-for="cat in categories"
          :key="cat.id"
          class="bg-white rounded-xl p-3 border border-base-200"
        >
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm">{{ cat.name }}</div>
              <div class="text-xs text-lumia-dark/40 mt-0.5" dir="ltr">{{ cat.slug }}</div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/50 flex-wrap">
                <span v-if="parentName(cat.parent) !== '—'">والد: {{ parentName(cat.parent) }}</span>
                <span v-if="cat.mood">· {{ cat.mood }}</span>
                <span>· ترتیب: {{ cat.sort_order }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="cat.is_active" @change="toggleActive(cat, $event)" />
              <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openModal(cat)">ویرایش</button>
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
                <th class="font-medium text-right">نام</th>
                <th class="font-medium text-right">والد</th>
                <th class="font-medium text-right">حالت</th>
                <th class="font-medium text-right">ترتیب</th>
                <th class="font-medium text-right">فعال</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="cat in categories" :key="cat.id" class="hover:bg-base-200/30">
                <td>
                  <div class="font-medium text-sm">{{ cat.name }}</div>
                  <div class="text-xs text-lumia-dark/40" dir="ltr">{{ cat.slug }}</div>
                </td>
                <td class="text-sm text-lumia-dark/60">{{ parentName(cat.parent) }}</td>
                <td class="text-sm text-lumia-dark/60">{{ cat.mood }}</td>
                <td class="text-sm text-lumia-dark/60">{{ cat.sort_order }}</td>
                <td><input type="checkbox" class="toggle toggle-success toggle-sm" :checked="cat.is_active" @change="toggleActive(cat, $event)" /></td>
                <td><button class="btn btn-ghost btn-xs text-lumia-gold" @click="openModal(cat)">ویرایش</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Modal -->
    <dialog ref="modalEl" class="modal">
      <div class="modal-box max-w-lg w-full mx-4">
        <h3 class="font-bold text-lumia-dark mb-4">{{ editing?.id ? 'ویرایش دسته‌بندی' : 'دسته‌بندی جدید' }}</h3>
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
            <label class="label-text text-xs block mb-1">والد</label>
            <select v-model="form.parent" class="select select-bordered w-full select-sm">
              <option :value="null">بدون والد</option>
              <option v-for="c in rootCategories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label-text text-xs block mb-1">حالت</label>
              <select v-model="form.mood" class="select select-bordered w-full select-sm">
                <option value="">—</option>
                <option value="perfume">عطر</option>
                <option value="skincare">مراقبت پوست</option>
                <option value="makeup">آرایشی</option>
              </select>
            </div>
            <div>
              <label class="label-text text-xs block mb-1">ترتیب</label>
              <input v-model.number="form.sort_order" type="number" class="input input-bordered w-full input-sm" dir="ltr" />
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">فعال</span>
          </label>
          <div class="modal-action gap-2 mt-4">
            <button type="button" class="btn btn-ghost btn-sm" @click="closeModal">لغو</button>
            <button v-if="editing?.id" type="button" class="btn btn-error btn-outline btn-sm" @click="deleteCategory">حذف</button>
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
const categories = ref<any[]>([])
const loading = ref(true)
const modalEl = ref<HTMLDialogElement | null>(null)
const editing = ref<any>(null)

const form = ref({ name: '', slug: '', parent: null as string | null, mood: '', sort_order: 0, is_active: true })

const rootCategories = computed(() => categories.value.filter(c => !c.parent))

function parentName(parentId: string | null) {
  if (!parentId) return '—'
  return categories.value.find(c => c.id === parentId)?.name ?? parentId
}

async function load() {
  loading.value = true
  const res = await apiFetch<any>('/admin/categories/')
  categories.value = res.results ?? res
  loading.value = false
}

function openModal(cat?: any) {
  editing.value = cat ?? null
  if (cat) {
    form.value = { name: cat.name, slug: cat.slug, parent: cat.parent, mood: cat.mood ?? '', sort_order: cat.sort_order ?? 0, is_active: cat.is_active }
  } else {
    form.value = { name: '', slug: '', parent: null, mood: '', sort_order: 0, is_active: true }
  }
  modalEl.value?.showModal()
}

function closeModal() {
  modalEl.value?.close()
}

async function save() {
  const body = { ...form.value, parent: form.value.parent || null }
  if (editing.value?.id) {
    const updated = await apiFetch<any>(`/admin/categories/${editing.value.id}/`, { method: 'PATCH', body })
    const idx = categories.value.findIndex(c => c.id === editing.value.id)
    if (idx !== -1) categories.value[idx] = updated
  } else {
    const created = await apiFetch<any>('/admin/categories/', { method: 'POST', body })
    categories.value.push(created)
  }
  closeModal()
}

async function deleteCategory() {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/categories/${editing.value.id}/`, { method: 'DELETE' })
  categories.value = categories.value.filter(c => c.id !== editing.value.id)
  closeModal()
}

async function toggleActive(cat: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/categories/${cat.id}/`, { method: 'PATCH', body: { is_active: val } })
  cat.is_active = val
}

onMounted(load)
</script>
