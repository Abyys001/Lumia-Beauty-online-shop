<template>
  <AdminBlogForm :is-new="true" />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: 'admin-auth' })
</script>
