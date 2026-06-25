<template>
  <div class="max-w-4xl space-y-4">
    <NuxtLink to="/admin/sms/dashboard" class="text-sm text-lumia-gold hover:underline">← داشبورد SMS</NuxtLink>

    <div v-if="loading" class="p-8 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <template v-else>
      <div class="bg-white rounded-2xl border border-base-200 overflow-hidden">
        <h2 class="font-bold p-4 border-b border-base-200">کدهای وضعیت API</h2>
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full text-sm">
            <thead class="bg-base-200/50"><tr><th>کد</th><th>توضیح</th></tr></thead>
            <tbody>
              <tr v-for="row in statusCodes" :key="row.code">
                <td dir="ltr" class="font-mono">{{ row.code }}</td>
                <td>{{ row.message }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="bg-white rounded-2xl border border-base-200 overflow-hidden">
        <h2 class="font-bold p-4 border-b border-base-200">وضعیت دلیوری</h2>
        <div class="overflow-x-auto w-full min-w-0">
          <table class="table w-full text-sm">
            <thead class="bg-base-200/50"><tr><th>کد</th><th>توضیح</th></tr></thead>
            <tbody>
              <tr v-for="row in deliveryStates" :key="row.code">
                <td dir="ltr" class="font-mono">{{ row.code }}</td>
                <td>{{ row.message }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { SmsErrorCodesResponse } from '~/types'

definePageMeta({ layout: 'admin', middleware: 'admin-auth' })

const { apiFetch } = useApi()
const loading = ref(true)
const statusCodes = ref<{ code: number; message: string }[]>([])
const deliveryStates = ref<{ code: number; message: string }[]>([])

onMounted(async () => {
  try {
    const res = await apiFetch<SmsErrorCodesResponse>('/admin/sms/error-codes/')
    statusCodes.value = res.status_codes
    deliveryStates.value = res.delivery_states
  } finally {
    loading.value = false
  }
})
</script>
