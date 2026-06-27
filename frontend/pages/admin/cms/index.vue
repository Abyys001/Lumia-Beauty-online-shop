<template>
  <div class="max-w-4xl space-y-8">
    <div class="flex items-center justify-between">
      <p class="text-sm text-lumia-dark/60">ویرایش بنر و نشان‌های اعتماد صفحه اصلی</p>
      <NuxtLink to="/" target="_blank" class="btn btn-ghost btn-sm text-lumia-gold">پیش‌نمایش سایت</NuxtLink>
    </div>

    <div v-if="loading" class="text-center py-12">در حال بارگذاری...</div>

    <template v-else>
      <form class="bg-white rounded-2xl p-6 border border-base-200 space-y-4" @submit.prevent="saveHero">
        <h2 class="font-bold text-lumia-dark">بنر Hero</h2>
        <input v-model="heroForm.headline" class="input input-bordered w-full rounded-xl" placeholder="تیتر اصلی" required />
        <input v-model="heroForm.subheadline" class="input input-bordered w-full rounded-xl" placeholder="تیتر فرعی" />
        <textarea v-model="heroForm.description" class="textarea textarea-bordered w-full rounded-xl" placeholder="توضیح" rows="3" />
        <input v-model="heroForm.badge_text" class="input input-bordered w-full rounded-xl" placeholder="برچسب بالای تیتر" />
        <div class="grid sm:grid-cols-2 gap-3">
          <input v-model="heroForm.cta_text" class="input input-bordered rounded-xl" placeholder="متن دکمه" />
          <input v-model="heroForm.cta_url" class="input input-bordered rounded-xl" placeholder="لینک دکمه" dir="ltr" />
          <input v-model="heroForm.cta_secondary_text" class="input input-bordered rounded-xl" placeholder="متن دکمه دوم" />
          <input v-model="heroForm.cta_secondary_url" class="input input-bordered rounded-xl" placeholder="لینک دکمه دوم" dir="ltr" />
        </div>
        <label class="flex items-center gap-2">
          <input v-model="heroForm.is_active" type="checkbox" class="checkbox checkbox-sm" />
          <span class="text-sm">فعال</span>
        </label>
        <button type="submit" class="btn btn-primary rounded-full" :disabled="savingHero">ذخیره بنر</button>
      </form>

      <div class="bg-white rounded-2xl p-6 border border-base-200">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-bold text-lumia-dark">نشان‌های اعتماد</h2>
          <button class="btn btn-outline btn-sm rounded-full" @click="addBadge">افزودن</button>
        </div>
        <div class="space-y-3">
          <div v-for="badge in badges" :key="badge.id" class="border border-base-200 rounded-xl p-4 grid sm:grid-cols-2 gap-3">
            <select v-model="badge.icon" class="select select-bordered select-sm rounded-xl">
              <option value="shield">تضمین اصالت</option>
              <option value="shipping">ارسال سریع</option>
              <option value="consult">مشاوره</option>
              <option value="payment">پرداخت امن</option>
              <option value="custom">سفارشی</option>
            </select>
            <input v-model="badge.title" class="input input-bordered input-sm rounded-xl" placeholder="عنوان" />
            <input v-model="badge.description" class="input input-bordered input-sm rounded-xl sm:col-span-2" placeholder="توضیح" />
            <div class="flex gap-2 sm:col-span-2">
              <button class="btn btn-primary btn-xs rounded-full" @click="saveBadge(badge)">ذخیره</button>
              <button class="btn btn-ghost btn-xs text-error" @click="deleteBadge(badge.id)">حذف</button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { AdminHomeHero, AdminTrustBadge } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const savingHero = ref(false)
const heroForm = reactive({
  headline: '',
  subheadline: '',
  description: '',
  badge_text: '',
  cta_text: '',
  cta_url: '/shop',
  cta_secondary_text: '',
  cta_secondary_url: '',
  is_active: true,
})
const badges = ref<AdminTrustBadge[]>([])

async function load() {
  loading.value = true
  try {
    const hero = await apiFetch<AdminHomeHero | null>('/admin/cms/hero/')
    if (hero) {
      Object.assign(heroForm, {
        headline: hero.headline,
        subheadline: hero.subheadline || '',
        description: hero.description || '',
        badge_text: hero.badge_text || '',
        cta_text: hero.cta_text || '',
        cta_url: hero.cta_url || '/shop',
        cta_secondary_text: hero.cta_secondary_text || '',
        cta_secondary_url: hero.cta_secondary_url || '',
        is_active: hero.is_active,
      })
    }
    badges.value = await apiFetch<AdminTrustBadge[]>('/admin/cms/trust-badges/')
  } finally {
    loading.value = false
  }
}

async function saveHero() {
  savingHero.value = true
  try {
    await apiFetch('/admin/cms/hero/', { method: 'PATCH', body: { ...heroForm } })
  } finally {
    savingHero.value = false
  }
}

async function saveBadge(badge: AdminTrustBadge) {
  await apiFetch(`/admin/cms/trust-badges/${badge.id}/`, {
    method: 'PATCH',
    body: { icon: badge.icon, title: badge.title, description: badge.description, is_active: badge.is_active },
  })
}

async function addBadge() {
  const created = await apiFetch<AdminTrustBadge>('/admin/cms/trust-badges/', {
    method: 'POST',
    body: { icon: 'shield', title: 'عنوان جدید', description: '', is_active: true },
  })
  badges.value.push(created)
}

async function deleteBadge(id: string) {
  if (!confirm('حذف شود؟')) return
  await apiFetch(`/admin/cms/trust-badges/${id}/`, { method: 'DELETE' })
  badges.value = badges.value.filter(b => b.id !== id)
}

onMounted(load)
</script>
