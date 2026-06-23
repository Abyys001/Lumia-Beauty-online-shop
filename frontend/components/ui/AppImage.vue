<template>
  <img
    :src="normalizedSrc"
    :alt="alt"
    :class="imgClass"
    :loading="priority ? 'eager' : loading"
    :fetchpriority="priority ? 'high' : 'auto'"
    decoding="async"
  />
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  src: string
  alt: string
  imgClass?: string
  loading?: 'lazy' | 'eager'
  priority?: boolean
  quality?: number
}>(), {
  imgClass: '',
  loading: 'lazy',
  priority: false,
  quality: 80,
})

const { normalizeMediaUrl } = useMediaUrl()

const normalizedSrc = computed(() => normalizeMediaUrl(props.src) || props.src)
</script>
