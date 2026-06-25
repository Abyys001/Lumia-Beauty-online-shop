<template>
  <img
    :src="normalizedSrc"
    :alt="alt"
    :class="imgClass"
    :style="imgStyle"
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
  imgStyle?: Record<string, string | number>
  loading?: 'lazy' | 'eager'
  priority?: boolean
  quality?: number
}>(), {
  imgClass: '',
  imgStyle: undefined,
  loading: 'lazy',
  priority: false,
  quality: 80,
})

const { normalizeMediaUrl } = useMediaUrl()

const normalizedSrc = computed(() => normalizeMediaUrl(props.src) || props.src)
</script>
