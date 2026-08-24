<template>
  <div class="bg-white p-6 rounded-3xl border border-lumia-cream shadow-sm space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between pb-4 border-b border-lumia-cream">
      <h3 class="font-bold text-lg text-lumia-dark">فیلترهای پیشرفته</h3>
      <button 
        class="text-xs text-lumia-gold hover:text-lumia-warm transition-colors font-medium"
        @click="$emit('reset')"
      >
        پاک کردن همه
      </button>
    </div>

    <!-- Categories -->
    <div class="space-y-3">
      <h4 class="font-semibold text-sm text-lumia-dark">دسته‌بندی‌ها</h4>
      <div class="space-y-2">
        <label 
          class="flex items-center justify-between text-sm cursor-pointer py-1 group"
          @click="update('category', '')"
        >
          <span :class="!filters.category ? 'text-lumia-gold font-semibold' : 'text-base-content/70 group-hover:text-lumia-dark'">همه محصولات</span>
          <span v-if="!filters.category" class="w-1.5 h-1.5 rounded-full bg-lumia-gold"></span>
        </label>
        <div v-for="cat in flatCategories" :key="cat.id" class="space-y-1">
          <label 
            class="flex items-center justify-between text-sm cursor-pointer py-1 group"
            @click="update('category', cat.slug)"
          >
            <span :class="filters.category === cat.slug ? 'text-lumia-gold font-semibold' : 'text-base-content/70 group-hover:text-lumia-dark'">
              {{ cat.name }}
            </span>
            <span v-if="filters.category === cat.slug" class="w-1.5 h-1.5 rounded-full bg-lumia-gold"></span>
          </label>
        </div>
      </div>
    </div>

    <!-- Brands -->
    <div class="space-y-3">
      <h4 class="font-semibold text-sm text-lumia-dark">برندها</h4>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="b in brands"
          :key="b.slug"
          class="px-3.5 py-1.5 rounded-full text-xs transition-all border"
          :class="filters.brand === b.slug 
            ? 'bg-lumia-gold border-lumia-gold text-lumia-dark font-semibold' 
            : 'bg-white border-lumia-cream text-base-content/80 hover:border-lumia-gold/50'"
          @click="update('brand', filters.brand === b.slug ? '' : b.slug)"
        >
          {{ b.name }}
        </button>

      </div>
    </div>

    <!-- Price Range -->
    <div class="space-y-3">
      <h4 class="font-semibold text-sm text-lumia-dark">محدوده قیمت (تومان)</h4>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <div>
          <label class="text-xxs text-base-content/50 block mb-1">از قیمت</label>
          <input
            :value="filters.min_price"
            type="number"
            placeholder="مثلا ۱۰۰,۰۰۰"
            class="input input-bordered input-sm w-full rounded-xl bg-lumia-cream/10 border-lumia-cream focus:border-lumia-gold focus:outline-none text-xs"
            @change="update('min_price', ($event.target as HTMLInputElement).value)"
          />
        </div>
        <div>
          <label class="text-xxs text-base-content/50 block mb-1">تا قیمت</label>
          <input
            :value="filters.max_price"
            type="number"
            placeholder="مثلا ۵,۰۰۰,۰۰۰"
            class="input input-bordered input-sm w-full rounded-xl bg-lumia-cream/10 border-lumia-cream focus:border-lumia-gold focus:outline-none text-xs"
            @change="update('max_price', ($event.target as HTMLInputElement).value)"
          />
        </div>
      </div>
    </div>

    <!-- Scent Notes -->
    <div class="space-y-3">
      <h4 class="font-semibold text-sm text-lumia-dark">نت‌های بویایی (عطر)</h4>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="note in scentNotes"
          :key="note"
          class="px-3 py-1.5 rounded-lg text-xs transition-all"
          :class="filters.scent === note
            ? 'bg-lumia-dark text-white font-medium'
            : 'bg-lumia-cream/30 text-base-content/70 hover:bg-lumia-cream/60'"
          @click="update('scent', filters.scent === note ? '' : note)"
        >
          {{ note }}
        </button>
      </div>
    </div>

    <!-- Skin Type -->
    <div class="space-y-3">
      <h4 class="font-semibold text-sm text-lumia-dark">نوع پوست (بهداشتی)</h4>
      <div class="flex flex-wrap gap-1.5">
        <button
          v-for="skin in skinTypes"
          :key="skin"
          class="px-3 py-1.5 rounded-lg text-xs transition-all"
          :class="filters.skin_type === skin
            ? 'bg-lumia-dark text-white font-medium'
            : 'bg-lumia-cream/30 text-base-content/70 hover:bg-lumia-cream/60'"
          @click="update('skin_type', filters.skin_type === skin ? '' : skin)"
        >
          {{ skin }}
        </button>
      </div>
    </div>

    <!-- Stock Availability -->
    <div class="pt-4 border-t border-lumia-cream">
      <label class="flex items-center gap-3 cursor-pointer group">
        <input
          type="checkbox"
          class="checkbox checkbox-primary checkbox-sm border-lumia-cream rounded-md checked:border-lumia-gold checked:bg-lumia-gold"
          :checked="filters.in_stock === 'true'"
          @change="update('in_stock', ($event.target as HTMLInputElement).checked ? 'true' : '')"
        />
        <span class="text-sm text-base-content/80 group-hover:text-lumia-dark select-none">فقط کالاهای موجود در انبار</span>
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '~/types'

const props = defineProps<{
  filters: Record<string, string>
  categories: Category[]
}>()

const emit = defineEmits<{
  update: [key: string, value: string]
  reset: []
}>()

function update(key: string, value: string) {
  emit('update', key, value)
}

// Flatten categories to easily list children under parents
const flatCategories = computed(() => {
  const list: Category[] = []
  props.categories.forEach(parent => {
    list.push(parent)
    if (parent.children && parent.children.length > 0) {
      parent.children.forEach(child => {
        list.push({
          ...child,
          name: `— ${child.name}`
        })
      })
    }
  })
  return list
})

const brands = ref<{ name: string; slug: string }[]>([])

onMounted(async () => {
  try {
    const { apiFetch } = useApi()
    brands.value = await apiFetch<{ name: string; slug: string }[]>('/brands/')
  } catch {
    // Better an empty brand list than demo brands that filter down to nothing.
    brands.value = []
  }
})

const scentNotes = ['خنک', 'گرم', 'تلخ', 'شیرین', 'مرکباتی', 'چوبی', 'گلی', 'چرمی']
const skinTypes = ['چرب', 'خشک', 'حساس', 'نرمال', 'انواع پوست']
</script>

<style scoped>
.text-xxs {
  font-size: 0.72rem;
}
</style>
