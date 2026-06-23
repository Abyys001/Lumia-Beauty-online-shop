<template>
  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="badgeClass">
    {{ label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ status: string }>()

const statusMap: Record<string, { label: string; class: string }> = {
  pending:      { label: 'در انتظار پرداخت', class: 'bg-gray-100 text-gray-600' },
  paid:         { label: 'پرداخت شده',       class: 'bg-green-100 text-green-700' },
  processing:   { label: 'در حال پردازش',   class: 'bg-blue-100 text-blue-700' },
  shipped:      { label: 'ارسال شده',        class: 'bg-indigo-100 text-indigo-700' },
  delivered:    { label: 'تحویل داده شده',   class: 'bg-purple-100 text-purple-700' },
  cancelled:    { label: 'لغو شده',          class: 'bg-red-100 text-red-700' },
  refunded:     { label: 'مرجوع شده',        class: 'bg-orange-100 text-orange-700' },
  success:      { label: 'موفق',             class: 'bg-green-100 text-green-700' },
  failed:       { label: 'ناموفق',           class: 'bg-red-100 text-red-700' },
  needs_review: { label: 'نیاز به بررسی',   class: 'bg-yellow-100 text-yellow-700' },
}

const entry = computed(() => statusMap[props.status] ?? { label: props.status, class: 'bg-gray-100 text-gray-600' })
const label = computed(() => entry.value.label)
const badgeClass = computed(() => entry.value.class)
</script>
