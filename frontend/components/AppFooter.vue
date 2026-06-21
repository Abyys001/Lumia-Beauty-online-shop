<template>
  <footer class="bg-neutral text-neutral-content mt-16">
    <div class="container-lumia py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <div class="flex items-center gap-3 mb-4">
            <img src="/logo.svg" alt="Lumia Beauty Logo" class="w-10 h-10 object-contain" />
            <h3 class="text-xl font-bold text-primary m-0">Lumia Beauty</h3>
          </div>
          <p class="text-neutral-content/70 leading-relaxed">
            فروشگاه آنلاین محصولات آرایشی، بهداشتی و خوش‌بوکننده با کیفیت اصل و ارسال سریع در سراسر ایران.
          </p>
        </div>
        <div>
          <h4 class="font-semibold mb-4">دسترسی سریع</h4>
          <ul class="space-y-2 text-neutral-content/70">
            <li><NuxtLink to="/shop" class="hover:text-primary transition-colors">فروشگاه</NuxtLink></li>
            <li><NuxtLink to="/blog" class="hover:text-primary transition-colors">وبلاگ</NuxtLink></li>
            <li><NuxtLink to="/account" class="hover:text-primary transition-colors">حساب کاربری</NuxtLink></li>
          </ul>
        </div>
        <div>
          <h4 class="font-semibold mb-4">تماس با ما</h4>
          <p class="text-neutral-content/70">اینستاگرام: @lumia.beauty</p>
          <p class="text-neutral-content/70 mt-2">پشتیبانی: ۰۹۱۲۰۰۰۰۰۰۰</p>
        </div>
      </div>
      <div class="border-t border-neutral-content/10 mt-8 pt-8 text-center text-neutral-content/50 text-sm">
        © {{ year }} Lumia Beauty — تمامی حقوق محفوظ است.
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const year = new Date().getFullYear()
</script>
