<template>
  <div class="py-16 md:py-24 bg-lumia-light/30">
    <div class="container-lumia max-w-5xl">
      <!-- Title -->
      <div class="text-center mb-16">
        <span class="text-xs uppercase tracking-widest text-lumia-gold font-bold">همواره پاسخگوی شما هستیم</span>
        <h1 class="text-4xl md:text-5xl font-black text-lumia-dark mt-2">تماس با لومیا بیوتی</h1>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-4"></div>
        <p class="text-base-content/70 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          سوالی دارید یا به مشاوره تخصصی نیاز دارید؟ از طریق فرم زیر یا راه‌های ارتباطی با ما در تماس باشید.
        </p>
      </div>

      <!-- Main Layout Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <!-- Contact Information (4 cols) -->
        <div class="lg:col-span-5 space-y-6">
          <div class="bg-white p-8 rounded-3xl border border-lumia-cream shadow-xs space-y-6">
            <h2 class="text-xl font-bold text-lumia-dark border-b border-lumia-cream pb-3">راه‌های ارتباطی</h2>
            
            <!-- Address -->
            <div class="flex items-start gap-4">
              <span class="text-2xl mt-1">📍</span>
              <div>
                <h3 class="font-bold text-sm text-lumia-dark">آدرس حضوری</h3>
                <p class="text-xs text-base-content/70 mt-1 leading-relaxed">
                  تهران، زعفرانیه، خیابان مقدس اردبیلی، مرکز خرید پالادیوم، طبقه اول، واحد ۱۲۴، لومیا بیوتی
                </p>
              </div>
            </div>

            <!-- Phone -->
            <div class="flex items-start gap-4">
              <span class="text-2xl mt-1">📞</span>
              <div>
                <h3 class="font-bold text-sm text-lumia-dark">تلفن پشتیبانی</h3>
                <p class="text-xs text-base-content/70 mt-1 dir-ltr text-right">
                  ۰۲۱-۲۲۶۶۰۱۲۰
                </p>
                <p class="text-xs text-base-content/70 mt-0.5 dir-ltr text-right">
                  ۰۹۱۲-۱۱۱۱۱۱۱
                </p>
              </div>
            </div>

            <!-- Working Hours -->
            <div class="flex items-start gap-4">
              <span class="text-2xl mt-1">⏰</span>
              <div>
                <h3 class="font-bold text-sm text-lumia-dark">ساعات کاری</h3>
                <p class="text-xs text-base-content/70 mt-1 leading-relaxed">
                  همه‌روزه از ساعت ۱۰:۰۰ صبح الی ۲۲:۰۰ شب (حتی در روزهای تعطیل)
                </p>
              </div>
            </div>

            <!-- Email -->
            <div class="flex items-start gap-4">
              <span class="text-2xl mt-1">✉️</span>
              <div>
                <h3 class="font-bold text-sm text-lumia-dark">پست الکترونیکی</h3>
                <p class="text-xs text-base-content/70 mt-1 font-mono">
                  support@lumiabeauty.com
                </p>
              </div>
            </div>
          </div>

          <!-- Quick Map Placeholder -->
          <div class="bg-lumia-cream/30 h-48 rounded-3xl border border-lumia-cream flex flex-col items-center justify-center text-center p-6 space-y-2 overflow-hidden relative">
            <div class="absolute inset-0 bg-lumia-dark/5 flex flex-col items-center justify-center">
              <span class="text-3xl">🗺️</span>
              <span class="text-xs font-bold text-lumia-dark mt-2">مرکز خرید پالادیوم، تهران</span>
              <span class="text-[10px] text-base-content/50">نمایش روی نقشه گوگل</span>
            </div>
          </div>
        </div>

        <!-- Contact Form (7 cols) -->
        <div class="lg:col-span-7 bg-white p-8 md:p-10 rounded-3xl border border-lumia-cream shadow-xs">
          <h2 class="text-xl font-bold text-lumia-dark border-b border-lumia-cream pb-3 mb-6">ارسال پیام مستقیم</h2>
          
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div v-if="success" class="alert alert-success rounded-2xl text-xs font-bold shadow-xs">
              <span>✓ پیام شما با موفقیت دریافت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Name -->
              <div class="form-control w-full">
                <label class="label"><span class="label-text text-xs font-bold">نام و نام خانوادگی</span></label>
                <input
                  type="text"
                  v-model="form.name"
                  required
                  placeholder="مثال: سارا کریمی"
                  class="input input-bordered w-full rounded-2xl text-xs bg-lumia-light/20 focus:border-lumia-gold focus:outline-none"
                />
              </div>
              <!-- Phone -->
              <div class="form-control w-full">
                <label class="label"><span class="label-text text-xs font-bold">شماره تماس (همراه)</span></label>
                <input
                  type="tel"
                  v-model="form.phone"
                  required
                  placeholder="مثال: 09123456789"
                  class="input input-bordered w-full rounded-2xl text-xs bg-lumia-light/20 focus:border-lumia-gold focus:outline-none"
                />
              </div>
            </div>

            <!-- Subject -->
            <div class="form-control w-full">
              <label class="label"><span class="label-text text-xs font-bold">موضوع پیام</span></label>
              <input
                type="text"
                v-model="form.subject"
                required
                placeholder="مثال: مشاوره خرید عطر زنانه"
                class="input input-bordered w-full rounded-2xl text-xs bg-lumia-light/20 focus:border-lumia-gold focus:outline-none"
              />
            </div>

            <!-- Message -->
            <div class="form-control w-full">
              <label class="label"><span class="label-text text-xs font-bold">متن پیام</span></label>
              <textarea
                v-model="form.message"
                required
                rows="5"
                placeholder="پیام خود را در این بخش بنویسید..."
                class="textarea textarea-bordered w-full rounded-2xl text-xs bg-lumia-light/20 focus:border-lumia-gold focus:outline-none"
              ></textarea>
            </div>

            <button
              type="submit"
              class="btn btn-primary rounded-full w-full font-bold text-xs mt-4"
              :disabled="loading"
            >
              <span v-if="loading" class="loading loading-spinner loading-xs"></span>
              <span>ارسال پیام</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const form = ref({
  name: '',
  phone: '',
  subject: '',
  message: '',
})

const loading = ref(false)
const success = ref(false)

async function handleSubmit() {
  loading.value = true
  success.value = false
  
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000))
  
  loading.value = false
  success.value = true
  form.value = {
    name: '',
    phone: '',
    subject: '',
    message: '',
  }
  
  // Hide success alert after 5 seconds
  setTimeout(() => {
    success.value = false
  }, 5000)
}

useSeoMeta({
  title: 'تماس با ما | لومیا بیوتی',
  description: 'راه‌های ارتباط با لومیا بیوتی. آدرس شعبه پالادیوم تهران، تلفن‌های پشتیبانی و فرم ارسال پیام مستقیم جهت دریافت مشاوره رایگان انتخاب عطر و روتین پوست.',
})
</script>
