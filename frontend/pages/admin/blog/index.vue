<template>
  <div class="min-w-0 max-w-full">
    <div class="flex justify-end mb-5">
      <NuxtLink to="/admin/blog/new" class="btn btn-primary btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        پست جدید
      </NuxtLink>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-base-200 overflow-hidden min-w-0">
      <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

      <template v-else>
        <div class="lg:hidden divide-y divide-base-200">
          <div v-for="post in posts" :key="post.id" class="px-4 py-3">
            <div class="font-medium text-sm">{{ post.title }}</div>
            <div class="text-xs text-lumia-dark/40 truncate" dir="ltr">{{ post.slug }}</div>
            <div class="flex flex-wrap items-center justify-between gap-2 mt-2">
              <span class="text-xs text-lumia-dark/50">{{ post.category_name || '—' }}</span>
              <label class="flex items-center gap-1 text-xs cursor-pointer">
                <input type="checkbox" class="toggle toggle-success toggle-xs" :checked="post.is_published" @change="togglePublish(post, $event)" />
                منتشر
              </label>
              <NuxtLink :to="`/admin/blog/${post.id}`" class="btn btn-ghost btn-xs text-lumia-gold mr-auto">ویرایش</NuxtLink>
            </div>
          </div>
        </div>

        <div class="hidden lg:block admin-table-wrap">
          <table class="table w-full">
            <thead class="bg-base-200/50">
              <tr class="text-lumia-dark/60 text-xs">
                <th class="font-medium text-right">عنوان</th>
                <th class="font-medium text-right">دسته‌بندی</th>
                <th class="font-medium text-right">وضعیت</th>
                <th class="font-medium text-right">تاریخ انتشار</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="post in posts" :key="post.id" class="hover:bg-base-200/30">
                <td>
                  <div class="font-medium text-sm">{{ post.title }}</div>
                  <div class="text-xs text-lumia-dark/40" dir="ltr">{{ post.slug }}</div>
                </td>
                <td class="text-sm text-lumia-dark/60">{{ post.category_name || '—' }}</td>
                <td>
                  <input type="checkbox" class="toggle toggle-success toggle-sm" :checked="post.is_published" @change="togglePublish(post, $event)" />
                </td>
                <td class="text-sm text-lumia-dark/50">{{ post.published_at ? formatDate(post.published_at) : '—' }}</td>
                <td>
                  <NuxtLink :to="`/admin/blog/${post.id}`" class="btn btn-ghost btn-xs text-lumia-gold">ویرایش</NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch, formatDate } = useApi()
const posts = ref<any[]>([])
const loading = ref(true)

async function load() {
  loading.value = true
  const res = await apiFetch<any>('/admin/blog/posts/')
  posts.value = res.results ?? res
  loading.value = false
}

async function togglePublish(post: any, e: Event) {
  const val = (e.target as HTMLInputElement).checked
  const body: Record<string, any> = { is_published: val }
  if (val && !post.published_at) body.published_at = new Date().toISOString()
  await apiFetch(`/admin/blog/posts/${post.id}/`, { method: 'PATCH', body })
  post.is_published = val
}

onMounted(load)
</script>
