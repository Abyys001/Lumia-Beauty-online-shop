<template>

  <div data-theme="lumia" class="min-h-screen flex flex-col overflow-x-clip w-full max-w-[100vw] bg-gradient-to-b from-lumia-cream/30 via-base-100 to-base-100">

    <AppHeader />

    <main class="flex-1 flex items-center justify-center w-full min-w-0 px-4 py-6 sm:py-10 min-h-[calc(100dvh-4rem)]">

      <slot />

    </main>

    <div class="mt-auto">

      <AppFooter />

    </div>

    <FloatingWhatsApp />

    <MobileNav />

  </div>

</template>


