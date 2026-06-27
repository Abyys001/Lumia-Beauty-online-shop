<template>
  <dialog ref="dialogEl" class="modal modal-bottom sm:modal-middle">
    <div class="modal-box p-0 max-w-2xl w-full rounded-3xl overflow-hidden shadow-2xl">
      <!-- Header -->
      <div class="relative bg-gradient-to-l from-lumia-dark via-lumia-dark/95 to-lumia-dark/90 px-5 sm:px-6 pt-5 pb-6 text-white">
        <button
          type="button"
          class="btn btn-ghost btn-sm btn-circle absolute top-3 left-3 text-white/60 hover:text-white hover:bg-white/10"
          :disabled="saving || deleting"
          @click="close"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="flex items-start gap-4 pe-8">
          <div class="w-14 h-14 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center shrink-0 overflow-hidden">
            <img
              v-if="previewImage"
              :src="previewImage"
              :alt="form.name || 'دسته‌بندی'"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-2xl">{{ moodEmoji(form.mood) }}</span>
          </div>
          <div class="flex-1 min-w-0 pt-0.5">
            <p class="text-white/50 text-xs mb-1">
              {{ isEditing ? 'ویرایش دسته‌بندی' : 'دسته‌بندی جدید' }}
            </p>
            <h3 class="font-bold text-lg sm:text-xl truncate">
              {{ form.name || 'بدون نام' }}
            </h3>
            <div class="flex flex-wrap items-center gap-2 mt-2">
              <span
                class="badge badge-sm border-0"
                :class="form.is_active ? 'bg-emerald-500/20 text-emerald-200' : 'bg-white/10 text-white/60'"
              >
                {{ form.is_active ? 'فعال' : 'غیرفعال' }}
              </span>
              <span v-if="form.slug" class="text-xs text-white/40 font-mono truncate max-w-[12rem]" dir="ltr">
                /{{ form.slug }}
              </span>
              <span v-if="childCount > 0" class="badge badge-sm bg-white/10 text-white/70 border-0">
                {{ childCount }} زیردسته
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete confirmation -->
      <div v-if="deleteStep" class="p-5 sm:p-6 space-y-4">
        <div class="flex items-start gap-3 rounded-2xl bg-error/10 border border-error/20 p-4">
          <div class="w-10 h-10 rounded-xl bg-error/15 flex items-center justify-center shrink-0 text-error">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <p class="font-semibold text-lumia-dark">حذف «{{ category?.name }}»</p>
            <p class="text-sm text-lumia-dark/60 mt-1 leading-relaxed">
              این عمل قابل بازگشت نیست.
              <template v-if="childCount > 0">
                با حذف این دسته، <strong>{{ childCount }} زیردسته</strong> نیز حذف می‌شوند.
              </template>
              اگر محصولی به این دسته متصل باشد، حذف انجام نمی‌شود.
            </p>
          </div>
        </div>

        <label class="flex items-center gap-3 cursor-pointer rounded-xl border border-base-200 p-3 hover:bg-base-200/40 transition-colors">
          <input v-model="deleteConfirmed" type="checkbox" class="checkbox checkbox-error checkbox-sm" />
          <span class="text-sm text-lumia-dark/80">متوجه عواقب هستم و می‌خواهم حذف کنم</span>
        </label>

        <div v-if="error" class="alert alert-error text-sm py-2">{{ error }}</div>

        <div class="flex flex-col-reverse sm:flex-row gap-2 pt-1">
          <button type="button" class="btn btn-ghost rounded-xl flex-1" :disabled="deleting" @click="cancelDelete">
            انصراف
          </button>
          <button
            type="button"
            class="btn btn-error rounded-xl flex-1 gap-2"
            :disabled="!deleteConfirmed || deleting"
            @click="confirmDelete"
          >
            <span v-if="deleting" class="loading loading-spinner loading-sm" />
            <span>{{ deleting ? 'در حال حذف...' : 'حذف قطعی' }}</span>
          </button>
        </div>
      </div>

      <!-- Form -->
      <form v-else class="p-5 sm:p-6" @submit.prevent="submit">
        <div role="tablist" class="tabs tabs-boxed bg-base-200/60 rounded-2xl p-1 mb-5 w-full">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            type="button"
            role="tab"
            class="tab flex-1 rounded-xl text-sm transition-all"
            :class="{ 'tab-active bg-white shadow-sm font-medium': activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Basic tab -->
        <div v-show="activeTab === 'basic'" class="space-y-4">
          <div class="grid sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
              <label class="text-xs font-medium text-lumia-dark/60 block mb-1.5">نام دسته‌بندی *</label>
              <input
                v-model="form.name"
                type="text"
                class="input input-bordered w-full rounded-xl focus:border-lumia-gold focus:outline-none"
                placeholder="مثلاً عطرهای زنانه"
                required
                @input="onNameInput"
              />
            </div>

            <div>
              <div class="flex items-center justify-between mb-1.5">
                <label class="text-xs font-medium text-lumia-dark/60">اسلاگ</label>
                <button
                  v-if="slugManual"
                  type="button"
                  class="text-[10px] text-lumia-gold hover:underline"
                  @click="resetSlugFromName"
                >
                  تولید خودکار
                </button>
              </div>
              <input
                v-model="form.slug"
                type="text"
                class="input input-bordered w-full rounded-xl font-mono text-sm focus:border-lumia-gold focus:outline-none"
                dir="ltr"
                placeholder="perfume-women"
                @input="slugManual = true"
              />
            </div>

            <div>
              <label class="text-xs font-medium text-lumia-dark/60 block mb-1.5">دسته والد</label>
              <select
                v-model="form.parent"
                class="select select-bordered w-full rounded-xl focus:border-lumia-gold focus:outline-none"
              >
                <option :value="null">بدون والد (سطح اصلی)</option>
                <option
                  v-for="opt in parentOptions"
                  :key="opt.id"
                  :value="opt.id"
                  :disabled="opt.disabled"
                >
                  {{ opt.label }}
                </option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-lumia-dark/60 block mb-2">حس / تم</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="m in moodOptions"
                :key="m.value"
                type="button"
                class="inline-flex items-center gap-2 px-3 py-2 rounded-xl border text-sm transition-all"
                :class="form.mood === m.value
                  ? 'border-lumia-gold bg-lumia-gold/10 text-lumia-dark shadow-sm'
                  : 'border-base-200 text-lumia-dark/70 hover:border-lumia-gold/40 hover:bg-base-200/50'"
                @click="form.mood = form.mood === m.value ? '' : m.value"
              >
                <span>{{ m.emoji }}</span>
                <span>{{ m.label }}</span>
              </button>
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-lumia-dark/60 block mb-1.5">توضیحات</label>
            <textarea
              v-model="form.description"
              class="textarea textarea-bordered w-full rounded-xl min-h-[88px] focus:border-lumia-gold focus:outline-none"
              placeholder="توضیح کوتاه برای نمایش در فروشگاه..."
            />
          </div>

          <div>
            <label class="text-xs font-medium text-lumia-dark/60 block mb-2">تصویر دسته‌بندی</label>
            <div class="flex flex-col sm:flex-row gap-4 items-start">
              <div
                v-if="previewImage"
                class="w-24 h-24 rounded-2xl overflow-hidden border border-base-200 shrink-0 shadow-sm"
              >
                <img :src="previewImage" class="w-full h-full object-cover" alt="" />
              </div>
              <div class="flex-1 w-full">
                <AdminImageUpload v-model="imageFile" label="تصویر را بکشید یا انتخاب کنید" />
              </div>
            </div>
          </div>

          <label class="flex items-center justify-between gap-4 rounded-2xl border border-base-200 p-4 cursor-pointer hover:bg-base-200/30 transition-colors">
            <div>
              <span class="text-sm font-medium text-lumia-dark block">نمایش در فروشگاه</span>
              <span class="text-xs text-lumia-dark/50">دسته‌های غیرفعال در سایت دیده نمی‌شوند</span>
            </div>
            <input v-model="form.is_active" type="checkbox" class="toggle toggle-success" />
          </label>
        </div>

        <!-- SEO tab -->
        <div v-show="activeTab === 'seo'" class="space-y-4">
          <div class="rounded-2xl bg-base-200/40 border border-base-200 p-4 text-sm text-lumia-dark/60 leading-relaxed">
            فیلدهای سئو برای بهینه‌سازی نمایش دسته‌بندی در موتورهای جستجو. در صورت خالی بودن، از نام و توضیحات استفاده می‌شود.
          </div>

          <div>
            <label class="text-xs font-medium text-lumia-dark/60 block mb-1.5">عنوان سئو</label>
            <input
              v-model="form.meta_title"
              type="text"
              class="input input-bordered w-full rounded-xl focus:border-lumia-gold focus:outline-none"
              placeholder="عنوان صفحه در گوگل"
              maxlength="200"
            />
            <p class="text-[10px] text-lumia-dark/40 mt-1 text-left" dir="ltr">{{ form.meta_title.length }}/200</p>
          </div>

          <div>
            <label class="text-xs font-medium text-lumia-dark/60 block mb-1.5">توضیحات سئو</label>
            <textarea
              v-model="form.meta_description"
              class="textarea textarea-bordered w-full rounded-xl min-h-[100px] focus:border-lumia-gold focus:outline-none"
              placeholder="توضیح متا برای موتورهای جستجو"
            />
          </div>

          <!-- SEO preview -->
          <div class="rounded-2xl border border-base-200 p-4 bg-white">
            <p class="text-[10px] uppercase tracking-wider text-lumia-dark/40 mb-2">پیش‌نمایش گوگل</p>
            <p class="text-[#1a0dab] text-base truncate">{{ seoPreviewTitle }}</p>
            <p class="text-[#006621] text-xs truncate mt-0.5" dir="ltr">lumia-beauty.ir/shop?category={{ form.slug || '...' }}</p>
            <p class="text-sm text-lumia-dark/60 mt-1 line-clamp-2">{{ seoPreviewDescription }}</p>
          </div>
        </div>

        <div v-if="error" class="alert alert-error text-sm py-2 mt-4">{{ error }}</div>

        <div class="flex flex-col-reverse sm:flex-row items-stretch sm:items-center gap-2 mt-6 pt-4 border-t border-base-200">
          <button
            v-if="isEditing"
            type="button"
            class="btn btn-ghost btn-sm text-error hover:bg-error/10 rounded-xl sm:me-auto"
            :disabled="saving"
            @click="startDelete"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            حذف
          </button>
          <div class="flex gap-2 sm:ms-auto">
            <button type="button" class="btn btn-ghost rounded-xl flex-1 sm:flex-none" :disabled="saving" @click="close">
              انصراف
            </button>
            <button type="submit" class="btn btn-primary rounded-xl flex-1 sm:flex-none min-w-[7rem] gap-2" :disabled="saving">
              <span v-if="saving" class="loading loading-spinner loading-sm" />
              <span>{{ saving ? 'در حال ذخیره...' : (isEditing ? 'ذخیره تغییرات' : 'ایجاد دسته') }}</span>
            </button>
          </div>
        </div>
      </form>
    </div>
    <form method="dialog" class="modal-backdrop bg-black/60 backdrop-blur-sm">
      <button type="button" @click="close">بستن</button>
    </form>
  </dialog>
</template>

<script setup lang="ts">
import type { AdminCategory } from '~/types'

const props = defineProps<{
  categories: AdminCategory[]
}>()

const emit = defineEmits<{
  saved: [category: AdminCategory]
  deleted: [id: string]
}>()

const { apiFetch } = useApi()
const { normalizeMediaUrl } = useMediaUrl()

const dialogEl = ref<HTMLDialogElement | null>(null)
const category = ref<AdminCategory | null>(null)
const imageFile = ref<File | null>(null)
const saving = ref(false)
const deleting = ref(false)
const error = ref('')
const activeTab = ref<'basic' | 'seo'>('basic')
const deleteStep = ref(false)
const deleteConfirmed = ref(false)
const slugManual = ref(false)

const tabs = [
  { id: 'basic' as const, label: 'اطلاعات پایه' },
  { id: 'seo' as const, label: 'سئو' },
]

const moodOptions = [
  { value: 'perfume', label: 'عطر', emoji: '🌸' },
  { value: 'skincare', label: 'مراقبت پوست', emoji: '✨' },
  { value: 'makeup', label: 'آرایشی', emoji: '💄' },
  { value: 'cool', label: 'خنک', emoji: '❄️' },
  { value: 'sweet', label: 'شیرین', emoji: '🍯' },
  { value: 'warm', label: 'گرم', emoji: '🔥' },
]

const emptyForm = () => ({
  name: '',
  slug: '',
  description: '',
  parent: null as string | null,
  mood: '',
  is_active: true,
  meta_title: '',
  meta_description: '',
})

const form = reactive(emptyForm())

const isEditing = computed(() => !!category.value?.id)
const childCount = computed(() => category.value?.children?.length ?? 0)

const filePreviewUrl = ref<string | null>(null)

watch(imageFile, (file, _prev, onCleanup) => {
  if (filePreviewUrl.value) {
    URL.revokeObjectURL(filePreviewUrl.value)
    filePreviewUrl.value = null
  }
  if (file) {
    filePreviewUrl.value = URL.createObjectURL(file)
    onCleanup(() => {
      if (filePreviewUrl.value) URL.revokeObjectURL(filePreviewUrl.value)
    })
  }
})

const previewImage = computed(() => {
  if (filePreviewUrl.value) return filePreviewUrl.value
  const url = category.value?.image
  return url ? normalizeMediaUrl(url) : null
})

const seoPreviewTitle = computed(() => form.meta_title || form.name || 'عنوان دسته‌بندی')
const seoPreviewDescription = computed(() =>
  form.meta_description || form.description || 'توضیحات دسته‌بندی در فروشگاه لومیا بیوتی...',
)

const parentOptions = computed(() => {
  const excludeIds = new Set<string>()
  if (category.value?.id) {
    excludeIds.add(category.value.id)
    const collect = (id: string) => {
      props.categories
        .filter(c => c.parent === id)
        .forEach(c => {
          excludeIds.add(c.id)
          collect(c.id)
        })
    }
    collect(category.value.id)
  }

  return props.categories
    .filter(c => !excludeIds.has(c.id))
    .map(c => {
      const depth = getDepth(c.parent)
      return {
        id: c.id,
        label: `${depth > 0 ? '— '.repeat(depth) : ''}${c.name}`,
        disabled: false,
      }
    })
})

function getDepth(parentId: string | null): number {
  if (!parentId) return 0
  const parent = props.categories.find(c => c.id === parentId)
  return parent ? 1 + getDepth(parent.parent) : 0
}

function moodEmoji(mood: string) {
  const found = moodOptions.find(m => m.value === mood)
  return found?.emoji ?? '📁'
}

function slugify(text: string): string {
  return text
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u0600-\u06FF-]+/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

function onNameInput() {
  if (!slugManual.value) {
    form.slug = slugify(form.name)
  }
}

function resetSlugFromName() {
  slugManual.value = false
  form.slug = slugify(form.name)
}

function resetState() {
  Object.assign(form, emptyForm())
  category.value = null
  imageFile.value = null
  if (filePreviewUrl.value) {
    URL.revokeObjectURL(filePreviewUrl.value)
    filePreviewUrl.value = null
  }
  error.value = ''
  saving.value = false
  deleting.value = false
  activeTab.value = 'basic'
  deleteStep.value = false
  deleteConfirmed.value = false
  slugManual.value = false
}

function open(cat?: AdminCategory) {
  resetState()
  if (cat) {
    category.value = cat
    Object.assign(form, {
      name: cat.name,
      slug: cat.slug,
      description: cat.description ?? '',
      parent: cat.parent,
      mood: cat.mood ?? '',
      is_active: cat.is_active,
      meta_title: cat.meta_title ?? '',
      meta_description: cat.meta_description ?? '',
    })
    slugManual.value = true
  }
  dialogEl.value?.showModal()
}

function close() {
  if (saving.value || deleting.value) return
  dialogEl.value?.close()
  resetState()
}

function startDelete() {
  deleteStep.value = true
  deleteConfirmed.value = false
  error.value = ''
}

function cancelDelete() {
  deleteStep.value = false
  deleteConfirmed.value = false
  error.value = ''
}

async function submit() {
  if (!form.name.trim()) {
    error.value = 'نام دسته‌بندی الزامی است'
    activeTab.value = 'basic'
    return
  }

  saving.value = true
  error.value = ''

  const payload: Record<string, unknown> = {
    name: form.name.trim(),
    slug: form.slug.trim() || slugify(form.name),
    description: form.description,
    parent: form.parent || null,
    mood: form.mood,
    is_active: form.is_active,
    meta_title: form.meta_title,
    meta_description: form.meta_description,
  }

  try {
    let result: AdminCategory
    if (imageFile.value) {
      const fd = new FormData()
      for (const [key, val] of Object.entries(payload)) {
        fd.append(key, val === null ? '' : String(val))
      }
      fd.append('image', imageFile.value)
      if (isEditing.value) {
        result = await apiFetch<AdminCategory>(`/admin/categories/${category.value!.id}/`, { method: 'PATCH', body: fd })
      } else {
        result = await apiFetch<AdminCategory>('/admin/categories/', { method: 'POST', body: fd })
      }
    } else if (isEditing.value) {
      result = await apiFetch<AdminCategory>(`/admin/categories/${category.value!.id}/`, { method: 'PATCH', body: payload })
    } else {
      result = await apiFetch<AdminCategory>('/admin/categories/', { method: 'POST', body: payload })
    }

    emit('saved', result)
    dialogEl.value?.close()
    resetState()
  } catch (e: unknown) {
    const err = e as { data?: Record<string, unknown> }
    error.value = extractErrorMessage(err.data) || 'خطا در ذخیره دسته‌بندی'
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  if (!category.value?.id || !deleteConfirmed.value) return

  deleting.value = true
  error.value = ''

  try {
    await apiFetch(`/admin/categories/${category.value.id}/`, { method: 'DELETE' })
    emit('deleted', category.value.id)
    dialogEl.value?.close()
    resetState()
  } catch (e: unknown) {
    const err = e as { data?: Record<string, unknown> }
    error.value = extractErrorMessage(err.data) || 'امکان حذف وجود ندارد. احتمالاً محصولی به این دسته متصل است.'
  } finally {
    deleting.value = false
  }
}

function extractErrorMessage(data?: Record<string, unknown>): string | null {
  if (!data) return null
  if (typeof data.detail === 'string') return data.detail
  for (const val of Object.values(data)) {
    if (typeof val === 'string') return val
    if (Array.isArray(val) && typeof val[0] === 'string') return val[0]
  }
  return null
}

defineExpose({ open })
</script>
