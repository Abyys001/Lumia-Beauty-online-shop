<template>
  <dialog ref="dialogEl" class="modal">
    <div class="modal-box max-w-lg rounded-3xl">
      <h3 class="font-bold text-lg mb-4">{{ editing ? 'ویرایش آدرس' : 'افزودن آدرس جدید' }}</h3>
      <form class="space-y-3" @submit.prevent="submit">
        <input v-model="form.title" class="input input-bordered w-full rounded-xl" placeholder="عنوان (مثلاً خانه)" required />
        <input v-model="form.receiver_name" class="input input-bordered w-full rounded-xl" placeholder="نام گیرنده" required />
        <input v-model="form.receiver_phone" class="input input-bordered w-full rounded-xl" placeholder="شماره موبایل گیرنده" dir="ltr" maxlength="11" required />
        <select v-model="form.province" class="select select-bordered w-full rounded-xl" required @change="form.city = ''">
          <option value="" disabled>استان</option>
          <option v-for="prov in provinceNames" :key="prov" :value="prov">{{ prov }}</option>
        </select>
        <select v-model="form.city" class="select select-bordered w-full rounded-xl" :disabled="!form.province" required>
          <option value="" disabled>شهر</option>
          <option v-for="city in availableCities" :key="city" :value="city">{{ city }}</option>
        </select>
        <input v-model="form.postal_code" class="input input-bordered w-full rounded-xl" placeholder="کد پستی" dir="ltr" maxlength="10" />
        <textarea v-model="form.address_line" class="textarea textarea-bordered w-full rounded-xl" placeholder="آدرس کامل" required />
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.is_default" type="checkbox" class="checkbox checkbox-primary checkbox-sm" />
          <span class="text-sm">آدرس پیش‌فرض</span>
        </label>
        <p v-if="error" class="text-error text-sm">{{ error }}</p>
        <div class="modal-action">
          <button type="button" class="btn btn-ghost rounded-full" @click="close">انصراف</button>
          <button type="submit" class="btn btn-primary rounded-full" :disabled="saving">
            <span v-if="saving" class="loading loading-spinner loading-sm" />
            <span v-else>ذخیره</span>
          </button>
        </div>
      </form>
    </div>
    <form method="dialog" class="modal-backdrop"><button @click="close">بستن</button></form>
  </dialog>
</template>

<script setup lang="ts">
import type { Address } from '~/types'

const emit = defineEmits<{ saved: [] }>()

const { apiFetch } = useApi()
const { provincesAndCities, citiesForProvince } = useIranProvinces()

const dialogEl = ref<HTMLDialogElement | null>(null)
const editing = ref(false)
const editId = ref('')
const saving = ref(false)
const error = ref('')

const emptyForm = () => ({
  title: 'خانه',
  receiver_name: '',
  receiver_phone: '',
  province: '',
  city: '',
  address_line: '',
  postal_code: '',
  is_default: false,
})

const form = reactive(emptyForm())

const provinceNames = computed(() => Object.keys(provincesAndCities))
const availableCities = computed(() => citiesForProvince(form.province))

function open(addr?: Address) {
  error.value = ''
  if (addr) {
    editing.value = true
    editId.value = addr.id
    Object.assign(form, {
      title: addr.title,
      receiver_name: addr.receiver_name,
      receiver_phone: addr.receiver_phone,
      province: addr.province,
      city: addr.city,
      address_line: addr.address_line,
      postal_code: addr.postal_code,
      is_default: addr.is_default,
    })
  } else {
    editing.value = false
    editId.value = ''
    Object.assign(form, emptyForm())
  }
  dialogEl.value?.showModal()
}

function close() {
  dialogEl.value?.close()
}

async function submit() {
  if (!/^\d{11}$/.test(form.receiver_phone)) {
    error.value = 'شماره موبایل باید ۱۱ رقم باشد'
    return
  }
  if (form.postal_code && !/^\d{10}$/.test(form.postal_code)) {
    error.value = 'کد پستی باید ۱۰ رقم باشد'
    return
  }
  saving.value = true
  error.value = ''
  try {
    if (editing.value) {
      await apiFetch(`/user/addresses/${editId.value}/`, { method: 'PATCH', body: { ...form } })
    } else {
      await apiFetch('/user/addresses/', { method: 'POST', body: { ...form } })
    }
    emit('saved')
    close()
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ذخیره آدرس'
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
