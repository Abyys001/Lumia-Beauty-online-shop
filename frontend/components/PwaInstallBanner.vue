<template>
  <ClientOnly>
    <Teleport to="body">
      <Transition name="pwa-banner">
        <div
          v-if="visible"
          class="pwa-install-banner"
          role="region"
          aria-label="نصب اپلیکیشن"
        >
          <button
            type="button"
            class="pwa-install-banner__close"
            aria-label="بستن"
            @click="dismiss"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4">
              <path stroke-linecap="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div class="pwa-install-banner__icon" aria-hidden="true">
            <img src="/favicon-192.png" alt="" width="40" height="40" class="rounded-xl">
          </div>

          <div class="pwa-install-banner__content">
            <p class="pwa-install-banner__title">لومیا بیوتی</p>
            <p v-if="isIOS" class="pwa-install-banner__text">
              برای نصب، دکمه
              <span class="font-bold">Share</span>
              را بزنید و
              <span class="font-bold">Add to Home Screen</span>
              را انتخاب کنید.
            </p>
            <p v-else class="pwa-install-banner__text">
              اپ را نصب کنید تا سریع‌تر به فروشگاه دسترسی داشته باشید.
            </p>
          </div>

          <button
            v-if="!isIOS && canInstall"
            type="button"
            class="btn btn-sm bg-lumia-gold text-lumia-dark border-0 hover:brightness-110 shrink-0"
            @click="install"
          >
            نصب اپ
          </button>
        </div>
      </Transition>
    </Teleport>
  </ClientOnly>
</template>

<script setup lang="ts">
const DISMISS_KEY = 'lumia_pwa_dismiss'
const DISMISS_MS = 7 * 24 * 60 * 60 * 1000

const route = useRoute()
const pwa = usePWA()

const isIOS = ref(false)
const dismissed = ref(true)
const canInstall = computed(() => !!pwa?.showInstallPrompt)

const isAdmin = computed(() => route.path.startsWith('/admin'))

const isInstalled = computed(() => {
  if (!import.meta.client) return false
  if (pwa?.isPWAInstalled) return pwa.isPWAInstalled
  return window.matchMedia('(display-mode: standalone)').matches
})

function readDismissed(): boolean {
  const raw = localStorage.getItem(DISMISS_KEY)
  if (!raw) return false
  const ts = Number.parseInt(raw, 10)
  if (Number.isNaN(ts)) return true
  if (Date.now() - ts > DISMISS_MS) {
    localStorage.removeItem(DISMISS_KEY)
    return false
  }
  return true
}

function dismiss() {
  localStorage.setItem(DISMISS_KEY, String(Date.now()))
  dismissed.value = true
}

async function install() {
  await pwa?.install()
}

const visible = computed(() => {
  if (!import.meta.client) return false
  if (isAdmin.value || isInstalled.value || dismissed.value) return false
  if (isIOS.value) return true
  return canInstall.value
})

onMounted(() => {
  const ua = navigator.userAgent
  isIOS.value = /iPhone|iPad|iPod/.test(ua) && !window.MSStream
  dismissed.value = readDismissed()
})
</script>

<style scoped>
.pwa-install-banner {
  position: fixed;
  z-index: 50;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  padding-bottom: max(0.875rem, env(safe-area-inset-bottom, 0px));
  background: linear-gradient(180deg, #2a2620 0%, #1c1a17 100%);
  border-top: 1px solid rgba(212, 175, 55, 0.25);
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.35);
}

.pwa-install-banner__close {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 9999px;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.15s ease, background 0.15s ease;
}

.pwa-install-banner__close:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.pwa-install-banner__icon {
  flex-shrink: 0;
  margin-inline-start: 1.5rem;
}

.pwa-install-banner__content {
  flex: 1;
  min-width: 0;
}

.pwa-install-banner__title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #d4af37;
  margin-bottom: 0.125rem;
}

.pwa-install-banner__text {
  font-size: 0.75rem;
  line-height: 1.4;
  color: rgba(255, 255, 255, 0.75);
}

.pwa-banner-enter-active,
.pwa-banner-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease;
}

.pwa-banner-enter-from,
.pwa-banner-leave-to {
  opacity: 0;
  transform: translateY(100%);
}

@media (min-width: 1024px) {
  .pwa-install-banner {
    display: none;
  }
}
</style>
