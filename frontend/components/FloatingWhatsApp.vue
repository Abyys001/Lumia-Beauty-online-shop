<template>
  <ClientOnly>
    <Teleport to="body">
      <Transition name="wa-fade">
        <a
          v-if="visible && !isAdmin"
          :href="whatsapp.url"
          target="_blank"
          rel="noopener noreferrer"
          class="floating-whatsapp group"
          :class="{ 'floating-whatsapp--expanded': expanded }"
          aria-label="چت در واتس‌اپ"
          @mouseenter="expanded = true"
          @mouseleave="expanded = false"
          @focus="expanded = true"
          @blur="expanded = false"
        >
          <span class="floating-whatsapp__pulse" aria-hidden="true" />
          <span class="floating-whatsapp__pulse floating-whatsapp__pulse--delayed" aria-hidden="true" />

          <span class="floating-whatsapp__icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="currentColor" class="w-7 h-7">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
          </span>

          <span class="floating-whatsapp__label">
            پیام در واتس‌اپ
          </span>
        </a>
      </Transition>
    </Teleport>
  </ClientOnly>
</template>

<script setup lang="ts">
const route = useRoute()
const { whatsapp } = useSocialLinks()

const visible = ref(false)
const expanded = ref(false)

const isAdmin = computed(() => route.path.startsWith('/admin'))

let showTimer: ReturnType<typeof setTimeout> | undefined

onMounted(() => {
  showTimer = setTimeout(() => {
    visible.value = true
  }, 1200)
})

onUnmounted(() => {
  if (showTimer) clearTimeout(showTimer)
})
</script>

<style scoped>
.floating-whatsapp {
  position: fixed;
  z-index: 45;
  bottom: max(1.25rem, env(safe-area-inset-bottom, 0px));
  left: max(1.25rem, env(safe-area-inset-left, 0px));
  display: flex;
  align-items: center;
  gap: 0;
  height: 3.5rem;
  width: 3.5rem;
  padding: 0;
  border-radius: 9999px;
  background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
  color: #fff;
  box-shadow:
    0 4px 14px rgba(37, 211, 102, 0.45),
    0 2px 6px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transition:
    width 0.35s cubic-bezier(0.16, 1, 0.3, 1),
    padding 0.35s cubic-bezier(0.16, 1, 0.3, 1),
    gap 0.35s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.floating-whatsapp:hover,
.floating-whatsapp:focus-visible {
  transform: scale(1.05);
  box-shadow:
    0 6px 20px rgba(37, 211, 102, 0.55),
    0 4px 10px rgba(0, 0, 0, 0.15);
  outline: none;
}

.floating-whatsapp--expanded {
  width: auto;
  padding-inline: 1.25rem 1rem;
  gap: 0.625rem;
}

.floating-whatsapp__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 3.5rem;
  height: 3.5rem;
}

.floating-whatsapp__label {
  max-width: 0;
  opacity: 0;
  white-space: nowrap;
  font-size: 0.8125rem;
  font-weight: 700;
  overflow: hidden;
  transition:
    max-width 0.35s cubic-bezier(0.16, 1, 0.3, 1),
    opacity 0.25s ease;
}

.floating-whatsapp--expanded .floating-whatsapp__label {
  max-width: 8rem;
  opacity: 1;
}

.floating-whatsapp__pulse {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: #25d366;
  opacity: 0.35;
  animation: wa-pulse 2.5s ease-out infinite;
  pointer-events: none;
}

.floating-whatsapp__pulse--delayed {
  animation-delay: 1.25s;
}

@keyframes wa-pulse {
  0% {
    transform: scale(1);
    opacity: 0.35;
  }
  70% {
    transform: scale(1.55);
    opacity: 0;
  }
  100% {
    transform: scale(1.55);
    opacity: 0;
  }
}

.wa-fade-enter-active {
  transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.wa-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.wa-fade-enter-from,
.wa-fade-leave-to {
  opacity: 0;
  transform: translateY(1rem) scale(0.85);
}

@media (max-width: 640px) {
  .floating-whatsapp {
    bottom: max(5.25rem, calc(env(safe-area-inset-bottom, 0px) + 4.25rem));
    left: max(1rem, env(safe-area-inset-left, 0px));
    height: 3.25rem;
    width: 3.25rem;
  }

  .floating-whatsapp__icon {
    width: 3.25rem;
    height: 3.25rem;
  }

  .floating-whatsapp__icon svg {
    width: 1.625rem;
    height: 1.625rem;
  }
}
</style>
