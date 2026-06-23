<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/admin/blog" class="btn btn-ghost btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        بازگشت
      </NuxtLink>
      <h2 class="font-bold text-lumia-dark">{{ isNew ? 'پست جدید' : 'ویرایش پست' }}</h2>
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else @submit.prevent="save" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main -->
      <div class="lg:col-span-2 space-y-4">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-4">
          <div>
            <label class="label-text text-xs block mb-1">عنوان *</label>
            <input v-model="form.title" type="text" class="input input-bordered w-full" required />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">اسلاگ</label>
            <input v-model="form.slug" type="text" class="input input-bordered w-full input-sm" dir="ltr" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">خلاصه (حداکثر ۵۰۰ کاراکتر)</label>
            <textarea v-model="form.excerpt" class="textarea textarea-bordered w-full" rows="3" maxlength="500" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">محتوای کامل *</label>
            <textarea v-model="form.content" class="textarea textarea-bordered w-full" rows="15" required />
          </div>
        </div>

        <!-- SEO -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-3">
          <h3 class="font-bold text-lumia-dark pb-3 border-b border-base-200">سئو</h3>
          <div>
            <label class="label-text text-xs block mb-1">عنوان متا</label>
            <input v-model="form.meta_title" type="text" class="input input-bordered w-full input-sm" />
          </div>
          <div>
            <label class="label-text text-xs block mb-1">توضیحات متا</label>
            <textarea v-model="form.meta_description" class="textarea textarea-bordered w-full textarea-sm" rows="2" />
          </div>
        </div>
      </div>

      <!-- Side -->
      <div class="space-y-4">
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-3">
          <h3 class="font-bold text-lumia-dark pb-3 border-b border-base-200">انتشار</h3>
          <label class="flex items-center justify-between cursor-pointer">
            <span class="text-sm">منتشر شده</span>
            <input v-model="form.is_published" type="checkbox" class="toggle toggle-success toggle-sm" />
          </label>
          <div v-if="form.is_published">
            <label class="label-text text-xs block mb-1">تاریخ انتشار</label>
            <input v-model="form.published_at" type="datetime-local" class="input input-bordered w-full input-sm" dir="ltr" />
          </div>
          <div class="flex gap-2 pt-2">
            <button type="submit" class="btn btn-primary flex-1" :class="{ loading: saving }">ذخیره</button>
          </div>
          <div v-if="!isNew">
            <button type="button" class="btn btn-error btn-outline w-full btn-sm" @click="deletePost">حذف پست</button>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200 space-y-3">
          <h3 class="font-bold text-lumia-dark pb-3 border-b border-base-200">دسته‌بندی و تگ</h3>
          <div>
            <label class="label-text text-xs block mb-1">دسته‌بندی</label>
            <select v-model="form.category" class="select select-bordered w-full select-sm">
              <option :value="null">بدون دسته‌بندی</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div>
            <label class="label-text text-xs block mb-1">تگ‌ها</label>
            <div class="flex flex-wrap gap-1">
              <label v-for="tag in tags" :key="tag.id" class="flex items-center gap-1 text-xs cursor-pointer bg-base-200 px-2 py-1 rounded-full" :class="{ 'bg-lumia-gold/20 text-lumia-gold': form.tag_ids.includes(tag.id) }">
                <input type="checkbox" class="hidden" :value="tag.id" v-model="form.tag_ids" />
                {{ tag.name }}
              </label>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-3 pb-3 border-b border-base-200">تصویر شاخص</h3>
          <AdminImageUpload label="آپلود تصویر" v-model="coverFile" />
          <img v-if="currentCover && !coverFile" :src="currentCover" class="w-full rounded-lg mt-3 border border-base-200 object-cover" style="max-height: 150px" />
        </div>
      </div>
    </form>

    <div v-if="error" class="alert alert-error mt-4 text-sm">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ postId?: string; isNew?: boolean }>()
const { apiFetch } = useApi()
const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const categories = ref<any[]>([])
const tags = ref<any[]>([])
const coverFile = ref<File | null>(null)
const currentCover = ref<string | null>(null)

const form = ref({
  title: '', slug: '', excerpt: '', content: '',
  category: null as string | null,
  tag_ids: [] as string[],
  is_published: false,
  published_at: '',
  meta_title: '', meta_description: '',
})

async function load() {
  const [cats, tgs] = await Promise.all([
    apiFetch<any>('/admin/blog/categories/'),
    apiFetch<any>('/admin/blog/tags/'),
  ])
  categories.value = cats.results ?? cats
  tags.value = tgs.results ?? tgs

  if (!props.isNew && props.postId) {
    const p = await apiFetch<any>(`/admin/blog/posts/${props.postId}/`)
    form.value = {
      title: p.title, slug: p.slug, excerpt: p.excerpt ?? '',
      content: p.content ?? '', category: p.category ?? null,
      tag_ids: p.tags?.map((t: any) => t.id) ?? [],
      is_published: p.is_published,
      published_at: p.published_at?.slice(0, 16) ?? '',
      meta_title: p.meta_title ?? '', meta_description: p.meta_description ?? '',
    }
    currentCover.value = p.cover_image
  }
  loading.value = false
}

async function save() {
  saving.value = true; error.value = ''
  try {
    let body: FormData | Record<string, any>
    if (coverFile.value) {
      const fd = new FormData()
      Object.entries(form.value).forEach(([k, v]) => {
        if (Array.isArray(v)) v.forEach(item => fd.append(k, item))
        else if (v !== null && v !== undefined) fd.append(k, String(v))
      })
      fd.append('cover_image', coverFile.value)
      body = fd
    } else {
      body = { ...form.value, published_at: form.value.published_at || null }
    }
    if (props.isNew) {
      const created = await apiFetch<any>('/admin/blog/posts/', { method: 'POST', body })
      router.push(`/admin/blog/${created.id}`)
    } else {
      await apiFetch(`/admin/blog/posts/${props.postId}/`, { method: 'PATCH', body })
    }
  } catch (e: any) {
    error.value = JSON.stringify(e.data) ?? 'خطا'
  } finally { saving.value = false }
}

async function deletePost() {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/blog/posts/${props.postId}/`, { method: 'DELETE' })
  router.push('/admin/blog')
}

onMounted(load)
</script>
