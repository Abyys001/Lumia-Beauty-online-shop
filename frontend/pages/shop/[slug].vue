<template>
  <div v-if="product" class="container-lumia py-8">
    <div class="grid md:grid-cols-2 gap-8 lg:gap-12">
      <!-- Right Column: Visuals & Gallery -->
      <div class="space-y-4">
        <!-- Main Image with Hover Zoom -->
        <div
          class="relative aspect-square rounded-3xl overflow-hidden bg-base-200 border border-base-200 cursor-zoom-in group"
          @mousemove="handleMouseMove"
          @mouseleave="handleMouseLeave"
        >
          <img
            v-if="selectedImage"
            :src="selectedImage"
            :alt="product.name"
            class="w-full h-full object-cover transition-transform duration-200 ease-out"
            :style="zoomStyle"
          />
        </div>
        
        <!-- Thumbnail Gallery -->
        <div v-if="product.images?.length > 1" class="flex gap-3 overflow-x-auto py-2">
          <button
            v-for="img in product.images"
            :key="img.id"
            class="w-20 h-20 rounded-xl overflow-hidden shrink-0 border-2 transition-all duration-200"
            :class="selectedImage === img.image ? 'border-primary scale-[1.03] shadow-md' : 'border-transparent opacity-70 hover:opacity-100'"
            @click="selectedImage = img.image"
          >
            <img :src="img.image" :alt="img.alt_text" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Left Column: Details -->
      <div class="space-y-6 text-right">
        <div>
          <NuxtLink v-if="product.brand" :to="`/shop?brand=${product.brand.slug}`" class="text-sm font-bold text-primary hover:underline mb-1 inline-block">
            {{ product.brand.name }}
          </NuxtLink>
          <h1 class="text-3xl font-extrabold text-base-content mb-2">{{ product.name }}</h1>
          <p v-if="product.slug" class="text-sm text-base-content/40 font-mono" style="letter-spacing: 0.5px;">{{ product.slug.replace(/-/g, ' ').toUpperCase() }}</p>
          
          <div class="flex items-center gap-2 mt-4 justify-start" style="flex-direction: row-reverse;">
            <span class="text-sm font-semibold text-base-content/60">({{ totalReviews }} نظر ثبت شده)</span>
            <div class="flex gap-0.5 text-warning" style="direction: ltr;">
              <span v-for="i in 5" :key="i" class="text-lg">
                {{ i <= Math.round(product.average_rating || 0) ? '★' : '☆' }}
              </span>
            </div>
            <span class="text-sm font-bold text-warning mr-1">{{ product.average_rating || '0.0' }}</span>
          </div>
        </div>

        <div class="divider my-2"></div>

        <!-- Price & Discounts -->
        <div class="space-y-2">
          <div class="flex items-center gap-3 justify-start" style="flex-direction: row-reverse;">
            <span v-if="product.discount_percent" class="badge badge-error font-bold py-3 px-3 mr-2">
              {{ product.discount_percent }}٪ تخفیف ویژه
            </span>
            <span v-if="product.compare_at_price" class="text-base-content/30 line-through text-lg">
              {{ formatPrice(product.compare_at_price) }}
            </span>
            <span class="text-3xl font-black text-primary">{{ formatPrice(product.price) }} تومان</span>
          </div>
          
          <!-- Stock Status Tag -->
          <div class="pt-2">
            <span v-if="product.stock > 5" class="inline-flex items-center gap-1.5 text-success font-bold text-sm bg-success/10 px-3 py-1.5 rounded-full" style="flex-direction: row-reverse;">
              <span class="w-2 h-2 rounded-full bg-success"></span>
              موجود در انبار لومیا بیوتی (آماده ارسال فوری)
            </span>
            <span v-else-if="product.stock > 0" class="inline-flex items-center gap-1.5 text-warning font-bold text-sm bg-warning/10 px-3 py-1.5 rounded-full" style="flex-direction: row-reverse;">
              <span class="w-2 h-2 rounded-full bg-warning animate-pulse"></span>
              موجودی محدود! (تنها {{ product.stock }} عدد باقی مانده)
            </span>
            <span v-else class="inline-flex items-center gap-1.5 text-error font-bold text-sm bg-error/10 px-3 py-1.5 rounded-full" style="flex-direction: row-reverse;">
              <span class="w-2 h-2 rounded-full bg-error"></span>
              ناموجود
            </span>
          </div>
        </div>

        <p class="text-base-content/70 leading-relaxed text-right" style="font-size: 0.95rem;">{{ product.short_description }}</p>

        <div class="divider my-2"></div>

        <!-- Add to Cart and quantity -->
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-4">
          <div class="flex items-center justify-between border border-base-300 rounded-xl px-2 py-1 bg-base-100 min-w-[130px]" style="flex-direction: row-reverse;">
            <button class="btn btn-ghost btn-sm text-lg font-bold" @click="quantity = Math.max(1, quantity - 1)">−</button>
            <span class="text-base font-bold w-12 text-center select-none">{{ quantity }}</span>
            <button class="btn btn-ghost btn-sm text-lg font-bold" @click="quantity = Math.min(product.stock, quantity + 1)">+</button>
          </div>
          
          <button
            class="btn-lumia flex-1 py-4 text-center font-bold text-base shadow-lg transition-transform hover:scale-[1.01]"
            :disabled="!product.is_in_stock || adding"
            @click="addToCart"
          >
            <span v-if="adding" class="loading loading-spinner loading-sm" />
            <span v-else-if="product.is_in_stock"><i class="fas fa-shopping-cart ml-2"></i> افزودن به سبد خرید</span>
            <span v-else>ناموجود</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Detailed Info & Specifications -->
    <div class="grid md:grid-cols-2 gap-10 mt-16 border-t border-base-200 pt-10">
      <div>
        <h2 class="text-xl font-bold mb-4 text-right">مشخصات فنی و ویژگی‌ها</h2>
        <div class="border border-base-200 rounded-2xl overflow-hidden">
          <table class="w-full text-right border-collapse">
            <tbody>
              <tr class="border-b border-base-200 bg-base-100/50">
                <td class="p-3 font-semibold text-sm w-1/3 text-base-content/60">برند محصول</td>
                <td class="p-3 text-sm font-medium">{{ product.brand?.name || 'لومیا بیوتی' }}</td>
              </tr>
              <tr class="border-b border-base-200">
                <td class="p-3 font-semibold text-sm text-base-content/60">دسته‌بندی اصلی</td>
                <td class="p-3 text-sm font-medium">{{ product.category?.name || 'دسته‌بندی لومیا' }}</td>
              </tr>
              <tr v-for="attr in product.attributes" :key="attr.key" class="border-b border-base-200 bg-base-100/30">
                <td class="p-3 font-semibold text-sm text-base-content/60">{{ attr.key_display }}</td>
                <td class="p-3 text-sm font-medium">{{ attr.value }}</td>
              </tr>
              <tr class="border-b border-base-200">
                <td class="p-3 font-semibold text-sm text-base-content/60">کد محصول (SKU)</td>
                <td class="p-3 text-sm font-medium font-mono">{{ product.sku || 'LB-' + product.id.substring(0,8).toUpperCase() }}</td>
              </tr>
              <tr>
                <td class="p-3 font-semibold text-sm text-base-content/60">ضمانت اصالت و سلامت</td>
                <td class="p-3 text-sm font-medium text-success"><i class="fas fa-shield-check ml-1"></i> تضمین اصالت و سلامت فیزیکی</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div>
        <h2 class="text-xl font-bold mb-4 text-right">توضیحات محصول</h2>
        <p class="text-base-content/70 leading-relaxed whitespace-pre-line text-right" style="font-size: 0.95rem;">{{ product.description }}</p>
      </div>
    </div>

    <!-- Reviews Section -->
    <div class="mt-16 border-t border-base-200 pt-10">
      <h2 class="text-2xl font-bold mb-8 text-right">نظرات کاربران</h2>
      
      <div class="grid md:grid-cols-3 gap-8">
        <!-- Star Rating Summary -->
        <div class="bg-base-100 p-6 rounded-2xl border border-base-200 text-right">
          <h3 class="font-bold text-lg mb-4">خلاصه امتیازات</h3>
          <div class="flex items-baseline gap-2 mb-2 justify-start" style="flex-direction: row-reverse;">
            <span class="text-4xl font-extrabold text-primary">{{ product.average_rating || '0.0' }}</span>
            <span class="text-base-content/50">از ۵</span>
          </div>
          <div class="flex gap-0.5 text-warning mb-4 justify-end" style="direction: ltr;">
            <span v-for="i in 5" :key="i" class="text-lg">
              {{ i <= Math.round(product.average_rating || 0) ? '★' : '☆' }}
            </span>
          </div>
          <p class="text-sm text-base-content/50 mb-6">بر اساس {{ totalReviews }} نظر ثبت شده</p>
          
          <!-- Rating Bars -->
          <div class="space-y-2">
            <div v-for="star in [5, 4, 3, 2, 1]" :key="star" class="flex items-center gap-2 text-sm" style="flex-direction: row-reverse;">
              <span class="w-3 text-right">{{ star }}</span>
              <span class="text-warning">★</span>
              <div class="flex-1 h-2 bg-base-200 rounded-full overflow-hidden">
                <div class="h-full bg-warning rounded-full" :style="{ width: `${percentage(star)}%` }"></div>
              </div>
              <span class="w-8 text-left text-base-content/50">{{ percentage(star) }}٪</span>
            </div>
          </div>
        </div>
        
        <!-- Review Form -->
        <div class="bg-base-100 p-6 rounded-2xl border border-base-200 text-right md:col-span-2">
          <h3 class="font-bold text-lg mb-4">ثبت نظر جدید</h3>
          
          <div v-if="auth.isAuthenticated">
            <form @submit.prevent="submitReview" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-base-content/70 mb-2">امتیاز شما به محصول:</label>
                <div class="flex gap-2 justify-end" style="direction: ltr;">
                  <button
                    v-for="star in 5"
                    :key="star"
                    type="button"
                    class="text-2xl transition-colors"
                    :class="newRating >= star ? 'text-warning' : 'text-base-content/20'"
                    @click="newRating = star"
                  >
                    ★
                  </button>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-base-content/70 mb-2">متن نظر:</label>
                <textarea
                  v-model="newComment"
                  rows="4"
                  class="textarea textarea-bordered w-full text-right"
                  placeholder="تجربه خود را از استفاده این محصول بنویسید..."
                  required
                ></textarea>
              </div>
              
              <div v-if="submitError" class="alert alert-error text-sm py-2">
                {{ submitError }}
              </div>
              <div v-if="submitSuccess" class="alert alert-success text-sm py-2">
                نظر شما با موفقیت ثبت شد و پس از تایید مدیریت نمایش داده می‌شود.
              </div>
              
              <button
                type="submit"
                class="btn btn-primary w-full md:w-auto px-6 font-bold"
                :disabled="submitting"
              >
                <span v-if="submitting" class="loading loading-spinner loading-sm"></span>
                <span v-else>ثبت و ارسال نظر</span>
              </button>
            </form>
          </div>
          
          <div v-else class="flex flex-col items-center justify-center py-8 text-center bg-base-200/30 rounded-xl border border-dashed border-base-300">
            <i class="fas fa-lock text-base-content/30 text-2xl mb-2"></i>
            <p class="text-base-content/60 text-sm mb-3">برای ثبت نظر، ابتدا باید وارد حساب کاربری خود شوید.</p>
            <NuxtLink to="/login" class="btn btn-primary btn-sm px-6 font-bold" style="border-radius: 8px;">ورود / ثبت‌نام</NuxtLink>
          </div>
        </div>
      </div>
      
      <!-- Existing Reviews List -->
      <div class="mt-10 space-y-6">
        <h3 class="font-bold text-lg text-right mb-4">نظرات اخیر کاربران</h3>
        <div v-if="product.reviews?.length" class="space-y-4">
          <div
            v-for="review in product.reviews"
            :key="review.id"
            class="bg-base-100 p-5 rounded-2xl border border-base-200 text-right"
          >
            <div class="flex justify-between items-center mb-3" style="flex-direction: row-reverse;">
              <div class="flex gap-0.5 text-warning" style="direction: ltr;">
                <span v-for="i in 5" :key="i">
                  {{ i <= review.rating ? '★' : '☆' }}
                </span>
              </div>
              <div class="text-right">
                <span class="font-semibold text-sm block" style="color: #2c3e50;">{{ review.user_name }}</span>
                <span class="text-xs text-base-content/40">{{ formatDate(review.created_at) }}</span>
              </div>
            </div>
            <p class="text-sm text-base-content/80 leading-relaxed">{{ review.comment }}</p>
          </div>
        </div>
        <p v-else class="text-center text-muted py-8 bg-base-100 rounded-2xl border border-base-200">اولین نفری باشید که برای این محصول نظر ثبت می‌کند!</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types'
import { useAuthStore } from '~/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const { apiFetch, formatPrice } = useApi()
const cart = useCartStore()

const quantity = ref(1)
const adding = ref(false)
const selectedImage = ref<string | null>(null)

// Zoom state
const isZoomed = ref(false)
const zoomX = ref(0)
const zoomY = ref(0)

// Review form state
const newRating = ref(5)
const newComment = ref('')
const submitting = ref(false)
const submitError = ref<string | null>(null)
const submitSuccess = ref(false)

const { data: product } = await useAsyncData(
  `product-${route.params.slug}`,
  () => apiFetch<Product>(`/products/${route.params.slug}/`),
)

if (product.value) {
  selectedImage.value = product.value.primary_image
    || product.value.images?.[0]?.image
    || null
}

// Hover Zoom Handlers
function handleMouseMove(e: MouseEvent) {
  const target = e.currentTarget as HTMLElement
  const { left, top, width, height } = target.getBoundingClientRect()
  const x = ((e.clientX - left) / width) * 100
  const y = ((e.clientY - top) / height) * 100
  zoomX.value = x
  zoomY.value = y
  isZoomed.value = true
}

function handleMouseLeave() {
  isZoomed.value = false
}

const zoomStyle = computed(() => {
  if (!isZoomed.value) return {}
  return {
    transform: 'scale(1.5)',
    transformOrigin: `${zoomX.value}% ${zoomY.value}%`
  }
})

// Review stats calculation
const totalReviews = computed(() => product.value?.reviews?.length || 0)

if (product.value) {
  useSeoMeta({
    title: product.value.meta_title || `${product.value.name} | لومیا بیوتی`,
    description: product.value.meta_description || product.value.short_description,
    ogTitle: product.value.name,
    ogDescription: product.value.short_description,
    ogImage: product.value.primary_image || undefined,
  })

  // Convert price to Rials if using IRR (Tomans to Rials is * 10)
  const priceInRials = computed(() => (product.value?.price || 0) * 10)

  // Map reviews for schema
  const schemaReviews = computed(() => {
    return product.value?.reviews?.map((r: any) => ({
      author: { name: r.user_name || 'کاربر لومیا بیوتی' },
      reviewRating: { ratingValue: r.rating },
      reviewBody: r.comment,
    })) || []
  })

  useSchemaOrg([
    defineProduct({
      name: product.value.name,
      description: product.value.short_description,
      image: product.value.primary_image,
      sku: product.value.sku || `LB-${product.value.id.substring(0, 8).toUpperCase()}`,
      brand: {
        name: product.value.brand?.name || 'لومیا اسنس',
      },
      offers: {
        price: priceInRials.value,
        priceCurrency: 'IRR',
        itemCondition: 'https://schema.org/NewCondition',
        availability: product.value.is_in_stock
          ? 'https://schema.org/InStock'
          : 'https://schema.org/OutOfStock',
      },
      aggregateRating: product.value.average_rating ? {
        ratingValue: product.value.average_rating,
        reviewCount: totalReviews.value || 1,
      } : undefined,
      review: schemaReviews.value.length ? schemaReviews.value : undefined,
    }),
    defineBreadcrumb({
      itemListElement: [
        { name: 'خانه', item: '/' },
        { name: 'فروشگاه', item: '/shop' },
        { name: product.value.category?.name || 'دسته‌بندی', item: `/shop?category=${product.value.category?.slug || ''}` },
        { name: product.value.name, item: route.path },
      ],
    }),
  ])
}

const ratingCounts = computed(() => {
  const counts = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 }
  if (!product.value?.reviews) return counts
  product.value.reviews.forEach(r => {
    if (r.rating >= 1 && r.rating <= 5) {
      counts[r.rating as keyof typeof counts]++
    }
  })
  return counts
})

const percentage = (star: number) => {
  if (totalReviews.value === 0) return 0
  return Math.round((ratingCounts.value[star as keyof typeof ratingCounts.value] / totalReviews.value) * 100)
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('fa-IR')
  } catch (e) {
    return dateStr
  }
}

async function addToCart() {
  if (!product.value) return
  adding.value = true
  try {
    await cart.addItem(product.value.id, quantity.value)
  } finally {
    adding.value = false
  }
}

async function submitReview() {
  if (!newComment.value.trim()) return
  submitting.value = true
  submitError.value = null
  submitSuccess.value = false
  
  try {
    await apiFetch(`/products/${product.value?.slug}/reviews/`, {
      method: 'POST',
      body: {
        rating: newRating.value,
        comment: newComment.value.trim()
      }
    })
    submitSuccess.value = true
    newComment.value = ''
    newRating.value = 5
    
    // Refresh product details
    const updatedProduct = await apiFetch<Product>(`/products/${product.value?.slug}/`)
    if (updatedProduct) {
      product.value = updatedProduct
    }
  } catch (err: any) {
    submitError.value = err.data?.detail || err.data?.non_field_errors?.[0] || 'خطایی در ثبت نظر رخ داد.'
  } finally {
    submitting.value = false
  }
}
</script>
