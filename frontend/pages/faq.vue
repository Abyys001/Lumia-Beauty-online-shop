<template>
  <div class="py-16 md:py-24 bg-lumia-light/30">
    <div class="container-lumia max-w-3xl">
      <!-- Title -->
      <div class="text-center mb-16">
        <span class="text-xs uppercase tracking-widest text-lumia-gold font-bold">پاسخ به سوالات شما</span>
        <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-black text-lumia-dark mt-2">سوالات متداول</h1>
        <div class="w-20 h-0.5 bg-lumia-gold mx-auto my-4"></div>
        <p class="text-base-content/70 max-w-2xl mx-auto text-sm md:text-base leading-relaxed">
          بیشترین سوالاتی که مشتریان گرامی لومیا بیوتی قبل یا بعد از خرید با آن‌ها مواجه می‌شوند را در این بخش پاسخ داده‌ایم.
        </p>
      </div>

      <!-- FAQ Container -->
      <div class="space-y-4">
        <!-- Section: Payment -->
        <h2 class="text-lg font-bold text-lumia-dark border-r-2 border-lumia-gold pr-3 my-6">۱. نحوه پرداخت سفارش</h2>

        <div class="rounded-3xl border-2 border-lumia-gold/40 bg-lumia-cream/40 p-5 sm:p-6">
          <p class="font-black text-lumia-dark mb-3">پرداخت در لومیا بیوتی کارت به کارت و با هماهنگی مستقیم فروشنده انجام می‌شود.</p>
          <ol class="space-y-2 text-sm font-bold text-lumia-dark/80 leading-7">
            <li>۱. محصولات را به سبد خرید اضافه کنید و فرم اطلاعات ارسال را تکمیل کنید.</li>
            <li>۲. پس از ثبت سفارش، یک <span class="text-lumia-gold">کد خرید ۶ رقمی</span> دریافت می‌کنید. آن را یادداشت کنید.</li>
            <li>۳. از طریق یکی از راه‌های پیامک، تلگرام، واتس‌اپ یا بله کد خرید را برای فروشنده بفرستید.</li>
            <li>۴. فروشنده شماره کارت را ارسال می‌کند؛ مبلغ فاکتور را واریز و رسید را همان‌جا بفرستید.</li>
            <li>۵. پس از تأیید فروشنده، سفارش شما بسته‌بندی و ارسال می‌شود.</li>
          </ol>
          <p class="mt-4 text-xs font-bold text-error">
            هرگز قبل از دریافت شماره کارت از فروشنده وجهی واریز نکنید.
          </p>
        </div>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" checked="checked" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            کد خرید خود را گم کرده‌ام، چه کار کنم؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>وارد حساب کاربری خود شوید و از بخش «سفارشات من» سفارش مورد نظر را باز کنید. کد خرید ۶ رقمی به همراه راهنمای کامل پرداخت در همان صفحه نمایش داده می‌شود.</p>
          </div>
        </div>

        <!-- Section: Authenticity -->
        <h2 class="text-lg font-bold text-lumia-dark border-r-2 border-lumia-gold pr-3 my-6">۲. اصالت کالا و کیفیت</h2>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            چگونه از اصالت ادکلن‌ها و محصولات بهداشتی در لومیا بیوتی مطمئن شوم؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>تمامی محصولات موجود در لومیا بیوتی دارای ضمانت ۱۰۰٪ اصالت فیزیکی و فاکتور رسمی شرکتی هستند. در صورت درخواست، بارکد و بچ‌کد (Batch Code) انحصاری محصول جهت استعلام از سایت‌های رسمی خارجی در اختیار شما قرار می‌گیرد. همچنین کلیه محصولات با پلمب اصلی کارخانه و هولوگرام رسمی تحویل داده می‌شوند.</p>
          </div>
        </div>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            بچ‌کد (Batch Code) محصولات در کدام قسمت قرار دارد؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>بچ‌کد معمولاً به صورت حک‌شده یا چاپ‌ شده با فونت متمایز، در کف جعبه بیرونی و همچنین کف شیشه عطر یا قوطی محصول بهداشتی قرار دارد. شما می‌توانید با وارد کردن این کد در وب‌سایت‌های معتبر جهانی مانند checkfresh.com تاریخ دقیق تولید و انقضای محصول را استعلام کنید.</p>
          </div>
        </div>

        <!-- Section: Shipping -->
        <h2 class="text-lg font-bold text-lumia-dark border-r-2 border-lumia-gold pr-3 my-6">۳. ارسال سفارش‌ها و هزینه‌ها</h2>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            مدت زمان ارسال سفارش‌ها در تهران و شهرستان چقدر است؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>سفارش‌های شهر تهران به انتخاب شما در بازه زمانی ۲ الی ۴ ساعته از طریق پیک اکسپرس یا در اولین روز کاری از طریق پست پیشتاز تحویل داده می‌شوند. سفارش‌های شهرستان نیز با پست پیشتاز ارسال شده و ظرف ۲ الی ۴ روز کاری به دستتان خواهند رسید.</p>
          </div>
        </div>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            هزینه ارسال چقدر است؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>هزینه ارسال برای همه سفارش‌ها در سراسر کشور به صورت ثابت ۱۵۰,۰۰۰ تومان است و در فاکتور شما به مبلغ اقلام اضافه می‌شود. این مبلغ شامل بسته‌بندی ایمن و ارسال پستی می‌شود.</p>
          </div>
        </div>

        <!-- Section: Return -->
        <h2 class="text-lg font-bold text-lumia-dark border-r-2 border-lumia-gold pr-3 my-6">۴. رویه‌های بازگشت کالا و عودت وجه</h2>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            آیا امکان مرجوع کردن کالا بعد از خرید وجود دارد؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>بله، در صورتی که پلمب محصول باز نشده باشد و جعبه آن در وضعیت اولیه خود قرار داشته باشد، شما تا ۷ روز تقویمی فرصت دارید درخواست مرجوعی خود را ثبت نمایید. توجه داشته باشید به دلیل رعایت پروتکل‌های بهداشتی، محصولات آرایشی و پوستی که پلمب یا برچسب اطمینان آن‌ها باز شده باشد، به هیچ عنوان قابل مرجوعی نیستند.</p>
          </div>
        </div>

        <div class="collapse collapse-arrow bg-white border border-lumia-cream rounded-3xl">
          <input type="radio" name="faq-accordion" />
          <div class="collapse-title text-sm font-bold text-lumia-dark">
            در صورت تایید مرجوعی، عودت وجه چقدر زمان می‌برد؟
          </div>
          <div class="collapse-content text-xs text-base-content/70 leading-relaxed">
            <p>پس از دریافت کالای مرجوعی توسط انبار لومیا بیوتی و تایید سلامت فیزیکی پلمب آن، مبلغ پرداختی شما ظرف حداکثر ۲۴ الی ۴۸ ساعت کاری به شماره کارت بانکی (به نام خریدار اولیه) واریز خواهد شد.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'سوالات متداول | لومیا بیوتی',
  description: 'پاسخ به سوالات پرتکرار مشتریان لومیا بیوتی در زمینه‌های ضمانت اصالت کالا، بررسی بچ‌کد، شیوه‌ها و زمان ارسال سفارشات، رویه بازگشت کالا و پرداخت وجه.',
})
</script>
