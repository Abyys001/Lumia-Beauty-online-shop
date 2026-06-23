<template>
  <div>
    <div class="flex justify-end mb-5">
      <button class="btn btn-primary btn-sm gap-2" @click="openModal()">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        پست جدید
      </button>
    </div>

    <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <div v-for="post in posts" :key="post.id" class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden group">
        <div class="aspect-square overflow-hidden bg-base-200">
          <img v-if="post.image" :src="post.image" class="w-full h-full object-cover" />
        </div>
        <div class="p-3">
          <p class="text-xs text-lumia-dark/60 truncate mb-2">{{ post.caption || '—' }}</p>
          <div class="flex items-center justify-between">
            <label class="flex items-center gap-1 cursor-pointer">
              <input type="checkbox" class="toggle toggle-success toggle-xs" :checked="post.is_active" @change="toggleActive(post, $event)" />
              <span class="text-xs">فعال</span>
            </label>
            <div class="flex gap-1">
              <button class="btn btn-ghost btn-xs text-lumia-gold" @click="openModal(post)">ویرایش</button>
              <button class="btn btn-ghost btn-xs text-error" @click="deletePost(post)">حذف</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <dialog ref="modalEl" class="modal">
      <div class="modal-box max-w-md">
        <h3 class="font-bold text-lumia-dark mb-4">{{ editing?.id ? 'ویرایش پست' : 'پست جدید' }}</h3>
        <form @submit.prevent="save" class="space-y-3">
          <div v-if="!editing?.id">
            <label class="label-text text-xs block mb-1">تصویر *</label>
            <AdminImageUpload label="آپلود تصویر پست" v-model="imageFile" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">لینک پست اینستاگرام</label>
            <input v-model="form.post_url" type="url" class="input input-bordered w-full input-sm" dir="ltr" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">کپشن</label>
            <textarea v-model="form.caption" class="textarea textarea-bordered w-full textarea-sm" rows="3" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">ترتیب</label>
            <input v-model.number="form.sort_order" type="number" class="input input-bordered w-full input-sm" dir="ltr" />
          </div>
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.is_active" type="checkbox" class="checkbox checkbox-sm" />
            <span class="text-sm">فعال</span>
          </label>
          <div class="modal-action gap-2 mt-4">
            <button type="button" class="btn btn-ghost btn-sm" @click="closeModal">لغو</button>
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
const posts = ref<any[]>([])
const loading = ref(true)
const modalEl = ref<HTMLDialogElement | null>(null)
const editing = ref<any>(null)
const imageFile = ref<File | null>(null)
const form = ref({ post_url: '', caption: '', sort_order: 0, is_active: true })

async function load() {
  loading.value = true
  const res = await apiFetch<any>('/admin/instagram/')
  posts.value = res.results ?? res
  loading.value = false
}

function openModal(post?: any) {
  editing.value = post ?? null
  imageFile.value = null
  form.value = post
    ? { post_url: post.post_url ?? '', caption: post.caption ?? '', sort_order: post.sort_order ?? 0, is_active: post.is_active }
    : { post_url: '', caption: '', sort_order: 0, is_active: true }
  modalEl.value?.showModal()
}

function closeModal() { modalEl.value?.close() }

async function save() {
  let body: FormData | Record<string, any>
  if (imageFile.value) {
    const fd = new FormData()
    fd.append('image', imageFile.value)
    fd.append('post_url', form.value.post_url)
    fd.append('caption', form.value.caption)
    fd.append('sort_order', String(form.value.sort_order))
    fd.append('is_active', String(form.value.is_active))
    body = fd
  } else {
    body = { ...form.value }
  }

  if (editing.value?.id) {
    const updated = await apiFetch<any>(`/admin/instagram/${editing.value.id}/`, { method: 'PATCH', body })
    const idx = posts.value.findIndex(p => p.id === editing.value.id)
    if (idx !== -1) posts.value[idx] = updated
  } else {
    const created = await apiFetch<any>('/admin/instagram/', { method: 'POST', body })
    posts.value.unshift(created)
  }
  closeModal()
}

async function deletePost(post: any) {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/instagram/${post.id}/`, { method: 'DELETE' })
  posts.value = posts.value.filter(p => p.id !== post.id)
}

async function toggleActive(post: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  await apiFetch(`/admin/instagram/${post.id}/`, { method: 'PATCH', body: { is_active: val } })
  post.is_active = val
}

onMounted(load)
</script>
