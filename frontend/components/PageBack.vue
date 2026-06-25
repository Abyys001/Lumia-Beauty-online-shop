<template>
  <NuxtLink
    v-if="target?.mode === 'link'"
    :to="target.to!"
    :class="buttonClass"
    :aria-label="target.label"
    :title="target.label"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
    </svg>
    <span v-if="variant === 'bar'">{{ target.label }}</span>
  </NuxtLink>
  <button
    v-else-if="target?.mode === 'history'"
    type="button"
    :class="buttonClass"
    :aria-label="target.label"
    :title="target.label"
    @click="router.back()"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
    </svg>
    <span v-if="variant === 'bar'">{{ target.label }}</span>
  </button>
</template>

<script setup lang="ts">
import type { PageBackTarget } from '~/composables/usePageBack'

const props = withDefaults(defineProps<{
  variant?: 'bar' | 'icon'
  to?: string
  label?: string
}>(), {
  variant: 'bar',
})

const router = useRouter()
const { back } = usePageBack()

const target = computed<PageBackTarget | null>(() => {
  if (props.to) {
    return { mode: 'link', to: props.to, label: props.label ?? 'بازگشت' }
  }
  return back.value
})

const buttonClass = computed(() => {
  if (props.variant === 'icon') {
    return 'btn btn-ghost btn-sm btn-square flex-shrink-0 text-lumia-dark hover:bg-base-200'
  }
  return 'inline-flex items-center gap-2 rounded-full border border-base-300 bg-white/90 px-4 py-2 text-sm font-semibold text-lumia-dark shadow-sm hover:border-primary hover:text-primary transition-colors'
})
</script>
