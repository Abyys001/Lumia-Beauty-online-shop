<template>
  <div>
    <label :for="id" class="flex items-baseline gap-1 text-sm font-medium text-base-content/80 mb-2">
      <span>{{ label }}</span>
      <span v-if="required" class="text-error font-bold" aria-hidden="true">*</span>
      <span v-if="required" class="sr-only">(الزامی)</span>
    </label>

    <slot />

    <p v-if="error" :id="`${id}-error`" class="flex items-start gap-1.5 text-error text-xs mt-1.5 leading-5" role="alert">
      <svg class="w-4 h-4 flex-shrink-0 mt-px" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      </svg>
      <span>{{ error }}</span>
    </p>
    <p v-else-if="hint" class="text-xs text-base-content/45 mt-1.5 leading-5">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
/** Label + hint + inline error wrapper, so every checkout field reports itself the same way. */
defineProps<{
  id: string
  label: string
  required?: boolean
  hint?: string
  error?: string
}>()
</script>
