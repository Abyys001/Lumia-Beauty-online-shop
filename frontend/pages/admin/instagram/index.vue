<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <p class="text-sm text-lumia-dark/60">
        پیج‌های اینستاگرام با برچسب اختصاصی در صفحه اصلی نمایش داده می‌شوند.
      </p>
      <button class="btn btn-primary btn-sm gap-2 rounded-full shrink-0" @click="openModal()">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        پیج جدید
      </button>
    </div>

    <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else-if="!pages.length" class="bg-white rounded-2xl border border-base-200 p-10 text-center text-lumia-dark/50">
      هنوز پیجی اضافه نشده. اولین پیج اینستاگرام را بسازید.
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div
        v-for="page in pages"
        :key="page.id"
        class="bg-white rounded-2xl shadow-sm border border-base-200 p-5 flex flex-col gap-4"
      >
        <div class="flex items-start gap-4">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center text-white shrink-0"
            style="background: linear-gradient(135deg, #833ab4 0%, #fd1d1d 50%, #fcb045 100%)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-lumia-dark truncate" dir="ltr">@{{ page.username }}</p>
            <p class="text-sm text-lumia-dark/70 mt-1">{{ page.label }}</p>
            <a
              :href="page.profile_url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-xs text-lumia-gold hover:underline mt-2 inline-block"
              dir="ltr"
            >
              {{ page.profile_url }}
            </a>
          </div>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-base-100">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              class="toggle toggle-success toggle-xs"
              :checked="page.is_active"
              @change="toggleActive(page, $event)"
            />
            <span class="text-xs">فعال</span>
          </label>
          <div class="flex gap-1">
            <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openModal(page)">ویرایش</button>
            <button class="btn btn-ghost btn-xs text-error" @click="deletePage(page)">حذف</button>
          </div>
        </div>
      </div>
    </div>

    <dialog ref="modalEl" class="modal">
      <div class="modal-box max-w-md">
        <h3 class="font-bold text-lumia-dark mb-4">{{ editing?.id ? 'ویرایش پیج' : 'پیج جدید' }}</h3>
        <form class="space-y-4" @submit.prevent="save">
          <div>
            <label class="label-text text-xs block mb-1">آیدی اینستاگرام *</label>
            <input
              v-model="form.username"
              type="text"
              class="input input-bordered w-full rounded-xl"
              placeholder="lumia.beauty"
              dir="ltr"
              required
            />
            <p class="text-xs text-lumia-dark/50 mt-1">بدون @ — فقط نام کاربری</p>
          </div>
          <div>
            <label class="label-text text-xs block mb-1">برچسب *</label>
            <input
              v-model="form.label"
              type="text"
              class="input input-bordered w-full rounded-xl"
              placeholder="فروش ادکلن این پیج"
              required
            />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">فعال</span>
          </label>
          <div class="modal-action gap-2 mt-2">
            <button type="button" class="btn btn-ghost btn-sm rounded-full" @click="closeModal">لغو</button>
            <button type="submit" class="btn btn-primary btn-sm rounded-full" :disabled="saving">
              {{ saving ? 'در حال ذخیره...' : 'ذخیره' }}
            </button>
          </div>
        </form>
      </div>
      <form method="dialog" class="modal-backdrop"><button @click="closeModal">بستن</button></form>
    </dialog>
  </div>
</template>

<script setup lang="ts">
import type { InstagramPage } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const pages = ref<InstagramPage[]>([])
const loading = ref(true)
const saving = ref(false)
const modalEl = ref<HTMLDialogElement | null>(null)
const editing = ref<InstagramPage | null>(null)
const form = ref({ username: '', label: '', is_active: true })

async function load() {
  loading.value = true
  try {
    const res = await apiFetch<InstagramPage[] | { results: InstagramPage[] }>('/admin/instagram/')
    pages.value = Array.isArray(res) ? res : (res.results ?? [])
  } finally {
    loading.value = false
  }
}

function openModal(page?: InstagramPage) {
  editing.value = page ?? null
  form.value = page
    ? {
        username: page.username,
        label: page.label,
        is_active: page.is_active ?? true,
      }
    : { username: '', label: '', is_active: true }
  modalEl.value?.showModal()
}

function closeModal() {
  modalEl.value?.close()
}

async function save() {
  saving.value = true
  try {
    const body = { ...form.value }
    if (editing.value?.id) {
      const updated = await apiFetch<InstagramPage>(`/admin/instagram/${editing.value.id}/`, {
        method: 'PATCH',
        body,
      })
      const idx = pages.value.findIndex(p => p.id === editing.value!.id)
      if (idx !== -1) pages.value[idx] = updated
    } else {
      const created = await apiFetch<InstagramPage>('/admin/instagram/', { method: 'POST', body })
      pages.value.push(created)
    }
    closeModal()
  } finally {
    saving.value = false
  }
}

async function deletePage(page: InstagramPage) {
  if (!confirm('این پیج حذف شود؟')) return
  await apiFetch(`/admin/instagram/${page.id}/`, { method: 'DELETE' })
  pages.value = pages.value.filter(p => p.id !== page.id)
}

async function toggleActive(page: InstagramPage, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/instagram/${page.id}/`, { method: 'PATCH', body: { is_active: val } })
  page.is_active = val
}

onMounted(load)
</script>
