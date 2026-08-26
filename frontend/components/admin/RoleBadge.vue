<template>
  <span
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium whitespace-nowrap"
    :class="role.class"
  >
    {{ role.label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ user: { is_staff: boolean; is_superuser: boolean; is_active: boolean } }>()

const role = computed(() => {
  if (!props.user.is_active) return { label: 'غیرفعال', class: 'bg-red-100 text-red-700' }
  if (props.user.is_superuser) return { label: 'مدیر ارشد', class: 'bg-amber-100 text-amber-800' }
  if (props.user.is_staff) return { label: 'ادمین', class: 'bg-indigo-100 text-indigo-700' }
  return { label: 'مشتری', class: 'bg-gray-100 text-gray-600' }
})
</script>
