<template>
  <section :class="sectionClass">
    <div class="container-lumia">
      <div v-if="title || subtitle" :class="['mb-8 sm:mb-12', centered ? 'text-center max-w-xl mx-auto' : '']">
        <p v-if="eyebrow" class="text-xs uppercase tracking-widest text-lumia-gold font-bold mb-2">{{ eyebrow }}</p>
        <h2 v-if="title" class="section-title text-2xl sm:text-3xl font-bold">{{ title }}</h2>
        <div v-if="title" class="w-20 h-0.5 bg-lumia-gold my-3" :class="centered ? 'mx-auto' : ''" />
        <p v-if="subtitle" class="section-subtitle text-sm text-base-content/70 mb-0">{{ subtitle }}</p>
      </div>
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title?: string
  subtitle?: string
  eyebrow?: string
  centered?: boolean
  sectionClass?: string
}>(), {
  centered: true,
  sectionClass: 'py-16 md:py-24',
})
</script>
