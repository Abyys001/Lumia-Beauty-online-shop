<template>
  <nav
    role="tablist"
    aria-label="بخش‌های حساب کاربری"
    :class="layout === 'grid' ? 'grid grid-cols-2 gap-2 lg:hidden' : 'hidden lg:flex lg:flex-col lg:gap-1'"
  >
    <button
      v-for="item in items"
      :key="item.id"
      role="tab"
      type="button"
      :aria-selected="modelValue === item.id"
      :class="navItemClass(item.id)"
      @click="emit('update:modelValue', item.id)"
    >
      <component :is="item.icon" class="w-5 h-5 shrink-0" aria-hidden="true" />
      <span>{{ item.label }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { h, type FunctionalComponent } from 'vue'

export type AccountTab = 'orders' | 'wishlist' | 'addresses' | 'profile'

const props = defineProps<{
  modelValue: AccountTab
  layout?: 'grid' | 'sidebar'
}>()

const emit = defineEmits<{ 'update:modelValue': [value: AccountTab] }>()

const IconOrders: FunctionalComponent = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  fill: 'none',
  viewBox: '0 0 24 24',
  stroke: 'currentColor',
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  }),
])

const IconWishlist: FunctionalComponent = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  fill: 'none',
  viewBox: '0 0 24 24',
  stroke: 'currentColor',
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z',
  }),
])

const IconAddresses: FunctionalComponent = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  fill: 'none',
  viewBox: '0 0 24 24',
  stroke: 'currentColor',
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z',
  }),
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M15 11a3 3 0 11-6 0 3 3 0 016 0z',
  }),
])

const IconProfile: FunctionalComponent = () => h('svg', {
  xmlns: 'http://www.w3.org/2000/svg',
  fill: 'none',
  viewBox: '0 0 24 24',
  stroke: 'currentColor',
}, [
  h('path', {
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
    'stroke-width': '2',
    d: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  }),
])

const items: { id: AccountTab; label: string; icon: FunctionalComponent }[] = [
  { id: 'orders', label: 'سفارشات', icon: IconOrders },
  { id: 'wishlist', label: 'علاقه‌مندی‌ها', icon: IconWishlist },
  { id: 'addresses', label: 'آدرس‌ها', icon: IconAddresses },
  { id: 'profile', label: 'پروفایل', icon: IconProfile },
]

function navItemClass(id: AccountTab) {
  const active = props.modelValue === id
  const base = props.layout === 'grid'
    ? 'flex flex-col items-center justify-center gap-1.5 min-h-[4.5rem] p-3 rounded-2xl border text-sm font-medium transition-colors'
    : 'flex items-center gap-3 w-full px-4 py-3 rounded-2xl border text-sm font-medium transition-colors text-right'
  const state = active
    ? 'bg-primary/10 border-primary text-primary font-semibold'
    : 'bg-white border-base-200 text-base-content hover:border-primary/40 hover:bg-base-100'
  return `${base} ${state}`
}
</script>
