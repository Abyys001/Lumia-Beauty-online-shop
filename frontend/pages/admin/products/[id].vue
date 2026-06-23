<template>
  <AdminProductForm :product-id="route.params.id as string" />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })
const route = useRoute()
</script>
