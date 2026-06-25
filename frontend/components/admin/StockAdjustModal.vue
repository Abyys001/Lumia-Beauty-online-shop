<template>
  <dialog ref="dialogEl" class="modal">
    <div class="modal-box max-w-md">
      <h3 class="font-bold text-lg mb-1">تعدیل موجودی</h3>
      <p class="text-sm text-lumia-dark/60 mb-4">{{ product?.name }}</p>
      <p class="text-sm mb-4">
        موجودی فعلی:
        <span class="font-bold">{{ product?.stock }} {{ product?.stock_unit_label || 'عدد' }}</span>
      </p>

      <div role="tablist" class="tabs tabs-boxed mb-4">
        <button
          v-for="t in tabs"
          :key="t.id"
          type="button"
          class="tab tab-sm"
          :class="{ 'tab-active': mode === t.id }"
          @click="mode = t.id"
        >
          {{ t.label }}
        </button>
      </div>

      <div v-if="mode === 'pack'" class="space-y-3">
        <div>
          <label class="label-text text-xs block mb-1">اندازه {{ product?.pack_label || 'شل' }}</label>
          <select v-model.number="packSize" class="select select-bordered w-full select-sm">
            <option v-for="size in packSizes" :key="size" :value="size">
              {{ size === 1 ? 'تکی (۱)' : `${size} ${product?.stock_unit_label || 'عدد'}` }}
            </option>
          </select>
        </div>
        <div>
          <label class="label-text text-xs block mb-1">تعداد {{ product?.pack_label || 'شل' }}</label>
          <div class="flex items-center gap-2">
            <button type="button" class="btn btn-outline btn-sm" @click="packCount = Math.max(-99, packCount - 1)">−</button>
            <input v-model.number="packCount" type="number" class="input input-bordered input-sm flex-1 text-center" dir="ltr" />
            <button type="button" class="btn btn-outline btn-sm" @click="packCount = Math.min(99, packCount + 1)">+</button>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="size in quickPackSizes"
            :key="size"
            type="button"
            class="btn btn-ghost btn-xs"
            @click="quickAddPack(size)"
          >
            +۱ {{ product?.pack_label }} ({{ size }})
          </button>
        </div>
      </div>

      <div v-else-if="mode === 'delta'" class="space-y-3">
        <div>
          <label class="label-text text-xs block mb-1">تغییر به {{ product?.stock_unit_label || 'عدد' }}</label>
          <div class="flex items-center gap-2">
            <button type="button" class="btn btn-outline btn-sm" @click="delta -= 1">−</button>
            <input v-model.number="delta" type="number" class="input input-bordered input-sm flex-1 text-center" dir="ltr" />
            <button type="button" class="btn btn-outline btn-sm" @click="delta += 1">+</button>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="btn btn-ghost btn-xs" @click="delta = 1">+۱</button>
          <button type="button" class="btn btn-ghost btn-xs" @click="delta = -1">−۱</button>
          <button type="button" class="btn btn-ghost btn-xs" @click="delta = 5">+۵</button>
        </div>
      </div>

      <div v-else class="space-y-3">
        <div>
          <label class="label-text text-xs block mb-1">موجودی دقیق</label>
          <input v-model.number="absoluteStock" type="number" min="0" class="input input-bordered w-full" dir="ltr" />
        </div>
      </div>

      <div class="rounded-xl bg-base-200/60 p-3 text-sm mt-4">
        <span v-if="mode === 'pack' && packCount !== 0">
          {{ Math.abs(packCount) }} {{ product?.pack_label }} × {{ packSize }} =
          <strong dir="ltr">{{ packCount > 0 ? '+' : '' }}{{ packSize * packCount }}</strong>
          {{ product?.stock_unit_label }}
        </span>
        <span v-else-if="mode === 'delta' && delta !== 0">
          تغییر: <strong dir="ltr">{{ delta > 0 ? '+' : '' }}{{ delta }}</strong>
        </span>
        <span v-else-if="mode === 'set'">
          تنظیم روی <strong>{{ absoluteStock }}</strong>
        </span>
        <span v-else class="text-lumia-dark/50">مقدار تغییر را وارد کنید</span>
        <div class="mt-1 text-lumia-dark/70">
          موجودی جدید: <strong>{{ previewStock }}</strong>
        </div>
      </div>

      <div class="mt-3">
        <label class="label-text text-xs block mb-1">یادداشت (اختیاری)</label>
        <input v-model="note" type="text" class="input input-bordered w-full input-sm" placeholder="مثلاً ورودی انبار..." />
      </div>

      <div v-if="error" class="alert alert-error text-sm mt-3">{{ error }}</div>

      <div class="modal-action">
        <button type="button" class="btn btn-ghost" @click="close">انصراف</button>
        <button type="button" class="btn btn-primary" :class="{ loading: saving }" @click="submit">ثبت</button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop"><button>بستن</button></form>
  </dialog>
</template>

<script setup lang="ts">
import type { InventoryProduct, StockAdjustPayload } from '~/types'

const props = defineProps<{
  product: InventoryProduct | null
}>()

const emit = defineEmits<{
  saved: []
}>()

const { apiFetch } = useApi()
const dialogEl = ref<HTMLDialogElement | null>(null)
const mode = ref<'pack' | 'delta' | 'set'>('pack')
const packSize = ref(12)
const packCount = ref(1)
const delta = ref(1)
const absoluteStock = ref(0)
const note = ref('')
const saving = ref(false)
const error = ref('')

const tabs = [
  { id: 'pack' as const, label: 'بسته / شل' },
  { id: 'delta' as const, label: 'تکی' },
  { id: 'set' as const, label: 'مقدار دقیق' },
]

const packSizes = computed(() => props.product?.effective_pack_sizes || [1, 6, 12])
const quickPackSizes = computed(() => packSizes.value.filter(s => s > 1))

const previewStock = computed(() => {
  const current = props.product?.stock ?? 0
  if (mode.value === 'pack') return Math.max(0, current + packSize.value * packCount.value)
  if (mode.value === 'delta') return Math.max(0, current + delta.value)
  return Math.max(0, absoluteStock.value)
})

function open(product: InventoryProduct) {
  mode.value = 'pack'
  packSize.value = product.effective_pack_sizes?.find(s => s > 1) || product.effective_pack_sizes?.[0] || 1
  packCount.value = 1
  delta.value = 1
  absoluteStock.value = product.stock
  note.value = ''
  error.value = ''
  dialogEl.value?.showModal()
}

function close() {
  dialogEl.value?.close()
}

function quickAddPack(size: number) {
  packSize.value = size
  packCount.value = 1
  submit()
}

async function submit() {
  if (!props.product) return
  saving.value = true
  error.value = ''

  const body: StockAdjustPayload = {
    product_id: props.product.id,
    mode: mode.value,
    note: note.value,
  }
  if (mode.value === 'pack') {
    body.pack_size = packSize.value
    body.pack_count = packCount.value
  } else if (mode.value === 'delta') {
    body.delta = delta.value
  } else {
    body.absolute_stock = absoluteStock.value
  }

  try {
    await apiFetch('/admin/inventory/adjust/', { method: 'POST', body })
    close()
    emit('saved')
  } catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    error.value = err.data?.detail || 'خطا در ثبت تغییر'
  } finally {
    saving.value = false
  }
}

defineExpose({ open })
</script>
