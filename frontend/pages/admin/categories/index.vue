<template>
  <div class="min-w-0 max-w-full">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
      <div>
        <p class="text-sm text-lumia-dark/50">{{ categories.length }} دسته‌بندی</p>
      </div>
      <button class="btn btn-primary btn-sm gap-2 rounded-xl shadow-sm" @click="openModal()">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        دسته‌بندی جدید
      </button>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl shadow-sm border border-base-200 p-10 text-center">
      <span class="loading loading-spinner loading-md text-lumia-gold" />
      <p class="text-lumia-dark/40 text-sm mt-3">در حال بارگذاری...</p>
    </div>

    <template v-else>
      <!-- Mobile cards -->
      <div class="lg:hidden space-y-2 mb-4">
        <button
          v-for="cat in categories"
          :key="cat.id"
          type="button"
          class="w-full text-right bg-white rounded-2xl p-4 border border-base-200 hover:border-lumia-gold/30 hover:shadow-sm transition-all active:scale-[0.99]"
          @click="openModal(cat)"
        >
          <div class="flex items-center gap-3">
            <div class="w-11 h-11 rounded-xl bg-base-200/80 flex items-center justify-center shrink-0 overflow-hidden text-lg">
              <img v-if="cat.image" :src="mediaUrl(cat.image)" class="w-full h-full object-cover" alt="" />
              <span v-else>{{ moodEmoji(cat.mood) }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-medium text-sm truncate">{{ cat.name }}</span>
                <span
                  class="badge badge-xs border-0 shrink-0"
                  :class="cat.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-base-200 text-lumia-dark/50'"
                >
                  {{ cat.is_active ? 'فعال' : 'غیرفعال' }}
                </span>
              </div>
              <div class="text-xs text-lumia-dark/40 mt-0.5 truncate" dir="ltr">{{ cat.slug }}</div>
              <div class="flex items-center gap-2 mt-1 text-xs text-lumia-dark/50">
                <span v-if="parentName(cat.parent) !== '—'">{{ parentName(cat.parent) }}</span>
                <span v-if="cat.mood">{{ moodLabel(cat.mood) }}</span>
              </div>
            </div>
            <div class="shrink-0" @click.stop>
              <input
                type="checkbox"
                class="toggle toggle-success toggle-sm"
                :checked="cat.is_active"
                @change="toggleActive(cat, $event)"
              />
            </div>
          </div>
        </button>
      </div>

      <!-- Desktop table -->
      <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden">
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right w-14" />
                <th class="font-medium text-right">نام</th>
                <th class="font-medium text-right">والد</th>
                <th class="font-medium text-right">حالت</th>
                <th class="font-medium text-right">وضعیت</th>
                <th class="font-medium text-right w-24">فعال</th>
                <th class="w-10" />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="cat in categories"
                :key="cat.id"
                class="hover:bg-lumia-gold/5 cursor-pointer group transition-colors"
                @click="openModal(cat)"
              >
                <td>
                  <div class="w-10 h-10 rounded-xl bg-base-200/80 flex items-center justify-center overflow-hidden text-base">
                    <img v-if="cat.image" :src="mediaUrl(cat.image)" class="w-full h-full object-cover" alt="" />
                    <span v-else>{{ moodEmoji(cat.mood) }}</span>
                  </div>
                </td>
                <td>
                  <div class="font-medium text-sm group-hover:text-lumia-gold transition-colors">{{ cat.name }}</div>
                  <div class="text-xs text-lumia-dark/40 font-mono" dir="ltr">{{ cat.slug }}</div>
                </td>
                <td class="text-sm text-lumia-dark/60">{{ parentName(cat.parent) }}</td>
                <td>
                  <span v-if="cat.mood" class="inline-flex items-center gap-1 text-sm text-lumia-dark/70">
                    <span>{{ moodEmoji(cat.mood) }}</span>
                    {{ moodLabel(cat.mood) }}
                  </span>
                  <span v-else class="text-lumia-dark/30">—</span>
                </td>
                <td>
                  <span
                    class="badge badge-sm border-0"
                    :class="cat.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-base-200 text-lumia-dark/50'"
                  >
                    {{ cat.is_active ? 'فعال' : 'غیرفعال' }}
                  </span>
                </td>
                <td @click.stop>
                  <input
                    type="checkbox"
                    class="toggle toggle-success toggle-sm"
                    :checked="cat.is_active"
                    @change="toggleActive(cat, $event)"
                  />
                </td>
                <td>
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-lumia-dark/20 group-hover:text-lumia-gold transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="!categories.length" class="bg-white rounded-2xl border border-dashed border-base-300 p-12 text-center">
        <div class="text-4xl mb-3">📁</div>
        <p class="font-medium text-lumia-dark mb-1">هنوز دسته‌بندی ندارید</p>
        <p class="text-sm text-lumia-dark/50 mb-4">اولین دسته‌بندی فروشگاه را بسازید</p>
        <button class="btn btn-primary btn-sm rounded-xl" @click="openModal()">ایجاد دسته‌بندی</button>
      </div>
    </template>

    <AdminCategoryFormModal
      ref="modalRef"
      :categories="categories"
      @saved="onSaved"
      @deleted="onDeleted"
    />
  </div>
</template>

<script setup lang="ts">
import type { AdminCategory } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const { normalizeMediaUrl } = useMediaUrl()

const categories = ref<AdminCategory[]>([])
const loading = ref(true)
const modalRef = ref<{ open: (cat?: AdminCategory) => void } | null>(null)

const moodMap: Record<string, { emoji: string; label: string }> = {
  perfume: { emoji: '🌸', label: 'عطر' },
  skincare: { emoji: '✨', label: 'مراقبت پوست' },
  makeup: { emoji: '💄', label: 'آرایشی' },
  cool: { emoji: '❄️', label: 'خنک' },
  sweet: { emoji: '🍯', label: 'شیرین' },
  warm: { emoji: '🔥', label: 'گرم' },
}

function mediaUrl(url: string | null | undefined) {
  return normalizeMediaUrl(url) ?? ''
}

function moodEmoji(mood?: string) {
  return moodMap[mood || '']?.emoji ?? '📁'
}

function moodLabel(mood: string) {
  return moodMap[mood]?.label ?? mood
}

function parentName(parentId: string | null) {
  if (!parentId) return '—'
  return categories.value.find(c => c.id === parentId)?.name ?? '—'
}

async function load() {
  loading.value = true
  try {
    const res = await apiFetch<{ results?: AdminCategory[] } | AdminCategory[]>('/admin/categories/')
    categories.value = Array.isArray(res) ? res : (res.results ?? [])
  } finally {
    loading.value = false
  }
}

function openModal(cat?: AdminCategory) {
  modalRef.value?.open(cat)
}

function onSaved(category: AdminCategory) {
  const idx = categories.value.findIndex(c => c.id === category.id)
  if (idx !== -1) {
    categories.value[idx] = category
  } else {
    categories.value.push(category)
  }
}

function onDeleted(id: string) {
  categories.value = categories.value.filter(c => c.id !== id)
}

async function toggleActive(cat: AdminCategory, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  const prev = cat.is_active
  cat.is_active = val
  try {
    await apiFetch(`/admin/categories/${cat.id}/`, { method: 'PATCH', body: { is_active: val } })
  } catch {
    cat.is_active = prev
    ;(e.target as HTMLInputElement).checked = prev
  }
}

onMounted(load)
</script>
