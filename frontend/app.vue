<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()

useHead({
  htmlAttrs: { lang: 'fa', dir: 'rtl' },
  link: [
    {
      rel: 'canonical',
      href: computed(() => {
        const path = route.path === '/' ? '' : route.path
        return `${config.public.siteUrl}${path}`
      })
    }
  ]
})
</script>
