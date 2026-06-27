<template>
  <div class="grid lg:grid-cols-[280px_1fr] gap-4 lg:gap-6 items-start">
    <aside class="space-y-4 lg:sticky lg:top-4">
      <slot name="header" />
      <div class="hidden lg:block bg-white rounded-3xl border border-base-200 shadow-sm p-3">
        <slot name="nav-sidebar" />
      </div>
      <slot name="nav-mobile" />
    </aside>
    <section class="min-w-0">
      <slot />
    </section>
  </div>
</template>
