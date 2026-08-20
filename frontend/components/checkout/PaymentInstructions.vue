<template>
  <div class="space-y-6 text-right">
    <!-- Purchase code — the single most important thing on this page -->
    <div class="relative overflow-hidden rounded-3xl border-2 border-lumia-gold bg-gradient-to-bl from-lumia-gold/20 via-lumia-cream to-lumia-light p-6 sm:p-8 shadow-lg">
      <div class="flex flex-col items-center gap-3 text-center">
        <span class="inline-flex items-center gap-2 rounded-full bg-lumia-dark px-4 py-1.5 text-xs font-bold text-lumia-light">
          <span class="relative flex h-2 w-2">
            <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-lumia-gold opacity-75" />
            <span class="relative inline-flex h-2 w-2 rounded-full bg-lumia-gold" />
          </span>
          سفارش ثبت شد — در انتظار پرداخت
        </span>

        <p class="text-base sm:text-lg font-bold text-lumia-dark">کد خرید شما</p>

        <p
          class="select-all font-mono text-4xl sm:text-6xl font-black tracking-[0.35em] text-lumia-dark drop-shadow-sm"
          dir="ltr"
        >
          {{ purchaseCode }}
        </p>

        <button
          type="button"
          class="btn btn-sm rounded-full bg-lumia-dark text-lumia-light border-0 hover:bg-lumia-warm gap-2 px-5"
          @click="copyCode"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          {{ copied ? 'کپی شد ✓' : 'کپی کد خرید' }}
        </button>

        <p class="text-sm font-bold text-error mt-1">
          این کد را یادداشت کنید — بدون آن سفارش شما قابل پیگیری نیست.
        </p>

        <p v-if="deadline" class="text-xs font-bold text-lumia-dark/60">
          مهلت پرداخت تا {{ deadline.date }}
          <span v-if="deadline.remaining">— {{ deadline.remaining }}</span>
        </p>
      </div>
    </div>

    <!-- Step-by-step instructions -->
    <div class="rounded-3xl border-2 border-lumia-dark/10 bg-white p-5 sm:p-7 shadow-sm">
      <h2 class="mb-1 text-xl sm:text-2xl font-black text-lumia-dark">
        چطور سفارشم را پرداخت کنم؟
      </h2>
      <p class="mb-5 text-sm text-lumia-dark/60">
        پرداخت این فروشگاه <strong class="text-lumia-dark">کارت به کارت</strong> و با هماهنگی مستقیم فروشنده انجام می‌شود. فقط ۴ قدم ساده:
      </p>

      <ol class="space-y-4">
        <li v-for="(step, i) in steps" :key="i" class="flex items-start gap-4">
          <span class="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-lumia-gold text-lg font-black text-lumia-dark">
            {{ toFa(i + 1) }}
          </span>
          <div class="flex-1 pt-1">
            <p class="font-bold text-lumia-dark leading-7" v-html="step" />
          </div>
        </li>
      </ol>

      <div class="mt-6 rounded-2xl border-r-4 border-error bg-error/5 p-4">
        <p class="text-sm font-bold text-error leading-7">
          ⚠️ هشدار مهم: هرگز قبل از دریافت شماره کارت از فروشنده، وجهی واریز نکنید. شماره کارت فقط از طریق همین راه‌های ارتباطی رسمی به شما اعلام می‌شود.
        </p>
      </div>
    </div>

    <!-- Contact channels -->
    <div class="rounded-3xl border-2 border-lumia-gold/40 bg-white p-5 sm:p-7 shadow-sm">
      <h2 class="mb-1 text-xl sm:text-2xl font-black text-lumia-dark">
        از یکی از این راه‌ها با فروشنده تماس بگیرید
      </h2>
      <p class="mb-5 text-sm text-lumia-dark/60">
        روی هر گزینه بزنید — برنامه باز می‌شود و متن پیام همراه با کد خرید شما از قبل آماده است. فقط دکمه ارسال را بزنید.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <component
          :is="channel.configured ? 'a' : 'div'"
          v-for="channel in channels"
          :key="channel.id"
          :href="channel.configured ? channel.url : undefined"
          :target="channel.id === 'sms' ? undefined : '_blank'"
          rel="noopener"
          class="group flex items-center gap-4 rounded-2xl border-2 p-4 transition-all"
          :class="channel.configured
            ? 'cursor-pointer border-base-200 bg-white hover:-translate-y-0.5 hover:shadow-lg'
            : 'cursor-not-allowed border-base-200 bg-base-200/40 opacity-50'"
          :style="channel.configured ? { borderColor: channel.color + '55' } : undefined"
        >
          <span
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-white transition-transform group-hover:scale-110"
            :style="{ backgroundColor: channel.color }"
          >
            <svg v-if="channel.id === 'sms'" class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <svg v-else-if="channel.id === 'telegram'" class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
            </svg>
            <svg v-else-if="channel.id === 'whatsapp'" class="h-6 w-6" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
            </svg>
            <svg v-else class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z" />
            </svg>
          </span>

          <span class="min-w-0 flex-1">
            <span class="block font-black text-lumia-dark">{{ channel.label }}</span>
            <span class="block truncate text-xs text-lumia-dark/50" dir="ltr">{{ channel.hint }}</span>
          </span>

          <svg v-if="channel.configured" class="h-5 w-5 shrink-0 text-lumia-dark/25 transition-transform group-hover:-translate-x-1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </component>
      </div>

      <div v-if="!anyChannel" class="mt-4 rounded-2xl bg-warning/10 border border-warning/30 p-4 text-sm font-bold text-warning">
        هنوز راه ارتباطی در تنظیمات فروشگاه ثبت نشده است. لطفاً از طریق صفحه «تماس با ما» با فروشنده در ارتباط باشید.
      </div>

      <!-- Copyable message, for customers who prefer to write manually -->
      <div class="mt-5 rounded-2xl bg-lumia-cream/50 border border-lumia-cream p-4">
        <p class="mb-2 text-xs font-bold text-lumia-dark/60">متن پیشنهادی پیام:</p>
        <p class="whitespace-pre-line text-sm text-lumia-dark leading-7">{{ message }}</p>
        <button type="button" class="btn btn-xs btn-outline rounded-full mt-3" @click="copyMessage">
          {{ messageCopied ? 'متن کپی شد ✓' : 'کپی متن پیام' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  purchaseCode: string
  total?: number
  expiresAt?: string | null
}>()

const { loadContact, buildChannels, buildMessage } = usePaymentChannels()

const copied = ref(false)
const messageCopied = ref(false)
// The remaining-days count depends on the clock, so it is client-only to keep SSR markup stable.
const mounted = ref(false)

// buildChannels reads the shared contact useState, so this re-computes once it loads.
const channels = computed(() => buildChannels(props.purchaseCode, props.total))
const anyChannel = computed(() => channels.value.some((c) => c.configured))
const message = computed(() => buildMessage(props.purchaseCode, props.total))

const deadline = computed(() => {
  if (!props.expiresAt) return null
  const at = new Date(props.expiresAt)
  if (Number.isNaN(at.getTime())) return null
  const days = Math.ceil((at.getTime() - Date.now()) / 86_400_000)
  return {
    date: at.toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' }),
    remaining: !mounted.value
      ? ''
      : days > 0
        ? `${days.toLocaleString('fa-IR')} روز باقی مانده`
        : 'مهلت به پایان رسیده است',
  }
})

const steps = computed(() => [
  'کد خرید بالا را <span class="text-lumia-gold">کپی</span> کنید.',
  'از میان راه‌های ارتباطی زیر یکی را انتخاب کنید و پیام را برای فروشنده بفرستید.',
  'فروشنده <span class="text-lumia-gold">شماره کارت</span> را برای شما ارسال می‌کند؛ مبلغ فاکتور را کارت به کارت واریز کنید.',
  'رسید واریز را همان‌جا برای فروشنده بفرستید. پس از تأیید، سفارش شما بسته‌بندی و ارسال می‌شود.',
])

function toFa(n: number) {
  return n.toLocaleString('fa-IR')
}

async function copyCode() {
  if (!import.meta.client) return
  await navigator.clipboard.writeText(props.purchaseCode)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function copyMessage() {
  if (!import.meta.client) return
  await navigator.clipboard.writeText(message.value)
  messageCopied.value = true
  setTimeout(() => { messageCopied.value = false }, 2000)
}

onMounted(() => {
  mounted.value = true
  loadContact()
})
</script>
