<template>
  <div class="bg-white rounded-2xl p-5 flex items-center gap-4 shadow-sm border border-base-200">
    <div
      class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
      :class="colorClass"
    >
      <slot name="icon" />
    </div>
    <div class="flex-1 min-w-0">
      <div class="text-lumia-dark/50 text-xs mb-1">{{ label }}</div>
      <div class="text-lumia-dark font-bold text-xl">{{ value }}</div>
      <div v-if="sub" class="text-lumia-dark/40 text-xs mt-0.5">{{ sub }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  sub?: string
  colorClass?: string
}>()
</script>
