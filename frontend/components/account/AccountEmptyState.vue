<template>
  <div class="flex flex-col items-center justify-center py-12 sm:py-16 px-6 bg-white rounded-3xl border border-lumia-cream shadow-sm text-center space-y-4">
    <div class="w-16 h-16 rounded-2xl bg-base-200 flex items-center justify-center text-3xl" aria-hidden="true">
      {{ icon }}
    </div>
    <div class="space-y-1">
      <h3 class="font-bold text-lg text-lumia-dark">{{ title }}</h3>
      <p v-if="description" class="text-sm text-base-content/60 max-w-sm">{{ description }}</p>
    </div>
    <NuxtLink
      v-if="to"
      :to="to"
      class="btn btn-primary rounded-full px-8"
    >
      {{ actionLabel }}
    </NuxtLink>
    <button
      v-else-if="actionLabel"
      type="button"
      class="btn btn-primary rounded-full px-8"
      @click="emit('action')"
    >
      {{ actionLabel }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description?: string
  actionLabel?: string
  to?: string
}>()

const emit = defineEmits<{ action: [] }>()
</script>
