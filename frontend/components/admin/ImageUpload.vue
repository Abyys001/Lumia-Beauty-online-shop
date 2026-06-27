<template>
  <div>
    <div
      class="border-2 border-dashed border-base-300 rounded-xl p-6 text-center cursor-pointer hover:border-lumia-gold transition-colors"
      :class="{ 'border-lumia-gold bg-lumia-gold/5': dragging, 'opacity-60 pointer-events-none': compressing }"
      @click="fileInput?.click()"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <span v-if="compressing" class="loading loading-spinner loading-md text-lumia-gold mb-2" />
      <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 mx-auto mb-2 text-lumia-dark/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <p class="text-lumia-dark/50 text-sm">{{ compressing ? 'در حال فشرده‌سازی...' : (label || 'تصویر را اینجا رها کنید یا کلیک کنید') }}</p>
      <p class="text-lumia-dark/30 text-xs mt-1">تصاویر به WebP فشرده و آپلود می‌شوند — حداکثر ۵ مگابایت</p>
      <p v-if="error" class="text-error text-xs mt-2">{{ error }}</p>
    </div>
    <input ref="fileInput" type="file" :accept="accept || 'image/*'" :multiple="multiple" class="hidden" @change="onFileChange" />

    <!-- Preview -->
    <div v-if="preview" class="mt-3 relative inline-block">
      <img :src="preview" class="w-24 h-24 object-cover rounded-lg border border-base-200" />
      <button
        type="button"
        class="absolute -top-2 -left-2 w-5 h-5 bg-error text-white rounded-full flex items-center justify-center text-xs"
        @click="clearPreview"
      >×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label?: string
  accept?: string
  multiple?: boolean
  modelValue?: File | null
}>()

const emit = defineEmits<{
  'update:modelValue': [File | null]
  'files': [File[]]
}>()

const { compressImageFile, compressImageFiles } = useImageCompress()

const fileInput = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
const compressing = ref(false)
const error = ref<string | null>(null)
const preview = ref<string | null>(null)

async function processFiles(files: File[]) {
  error.value = null
  compressing.value = true
  try {
    if (props.multiple) {
      const compressed = await compressImageFiles(files)
      emit('files', compressed)
    } else {
      const file = files[0]
      const compressed = await compressImageFile(file)
      emit('update:modelValue', compressed)
      preview.value = URL.createObjectURL(compressed)
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'خطا در پردازش تصویر'
  } finally {
    compressing.value = false
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files?.length) return
  processFiles(Array.from(files))
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const files = e.dataTransfer?.files
  if (!files?.length) return
  processFiles(Array.from(files))
}

function clearPreview() {
  preview.value = null
  emit('update:modelValue', null)
  if (fileInput.value) fileInput.value.value = ''
}
</script>
