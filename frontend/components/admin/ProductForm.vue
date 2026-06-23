<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <NuxtLink to="/admin/products" class="btn btn-ghost btn-sm gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        بازگشت
      </NuxtLink>
      <h2 class="font-bold text-lumia-dark">{{ isNew ? 'محصول جدید' : 'ویرایش محصول' }}</h2>
    </div>

    <div v-if="loading" class="p-12 text-center text-lumia-dark/40">در حال بارگذاری...</div>

    <form v-else @submit.prevent="save" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main column -->
      <div class="lg:col-span-2 space-y-4">
        <!-- Basic info -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">اطلاعات اصلی</h3>
          <div class="space-y-4">
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">نام محصول *</label>
              <input v-model="form.name" type="text" class="input input-bordered w-full" required />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">اسلاگ (slug)</label>
              <input v-model="form.slug" type="text" class="input input-bordered w-full input-sm" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">توضیح کوتاه</label>
              <textarea v-model="form.short_description" class="textarea textarea-bordered w-full" rows="2" />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">توضیحات کامل</label>
              <textarea v-model="form.description" class="textarea textarea-bordered w-full" rows="5" />
            </div>
          </div>
        </div>

        <!-- Price & Stock -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">قیمت و انبار</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">قیمت اصلی (تومان) *</label>
              <input v-model.number="form.original_price" type="number" min="0" class="input input-bordered w-full" dir="ltr" required />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">قیمت فروش (تومان) *</label>
              <input v-model.number="form.discounted_price" type="number" min="0" class="input input-bordered w-full" dir="ltr" required />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">موجودی انبار</label>
              <input v-model.number="form.stock" type="number" min="0" class="input input-bordered w-full" dir="ltr" />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">کد SKU</label>
              <input v-model="form.sku" type="text" class="input input-bordered w-full" dir="ltr" />
            </div>
          </div>
        </div>

        <!-- Attributes -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">ویژگی‌های محصول</h3>
          <div v-for="(attr, i) in form.attributes" :key="i" class="flex gap-2 mb-2">
            <select v-model="attr.key" class="select select-bordered select-sm flex-shrink-0 w-40">
              <option value="scent">رایحه</option>
              <option value="skin_type">نوع پوست</option>
              <option value="volume">حجم</option>
              <option value="product_type">نوع محصول</option>
            </select>
            <input v-model="attr.value" type="text" class="input input-bordered input-sm flex-1" placeholder="مقدار" />
            <button type="button" class="btn btn-ghost btn-sm text-error" @click="removeAttr(i)">×</button>
          </div>
          <button type="button" class="btn btn-ghost btn-sm gap-2 mt-2" @click="addAttr">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            افزودن ویژگی
          </button>
        </div>

        <!-- SEO -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">سئو</h3>
          <div class="space-y-3">
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">عنوان متا</label>
              <input v-model="form.meta_title" type="text" class="input input-bordered w-full input-sm" />
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">توضیحات متا</label>
              <textarea v-model="form.meta_description" class="textarea textarea-bordered w-full textarea-sm" rows="2" />
            </div>
          </div>
        </div>
      </div>

      <!-- Side column -->
      <div class="space-y-4">
        <!-- Publish -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">انتشار</h3>
          <div class="space-y-3">
            <label class="flex items-center justify-between cursor-pointer">
              <span class="text-sm">فعال</span>
              <input v-model="form.is_active" type="checkbox" class="toggle toggle-success toggle-sm" />
            </label>
            <label class="flex items-center justify-between cursor-pointer">
              <span class="text-sm">محصول ویژه</span>
              <input v-model="form.is_featured" type="checkbox" class="toggle toggle-warning toggle-sm" />
            </label>
          </div>
          <div class="mt-4 flex gap-2">
            <button type="submit" class="btn btn-primary flex-1" :class="{ loading: saving }">
              {{ isNew ? 'ایجاد محصول' : 'ذخیره تغییرات' }}
            </button>
          </div>
          <div v-if="!isNew" class="mt-2">
            <button type="button" class="btn btn-error btn-outline w-full btn-sm" @click="deleteProduct">حذف محصول</button>
          </div>
        </div>

        <!-- Category & Brand -->
        <div class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">دسته‌بندی و برند</h3>
          <div class="space-y-3">
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">دسته‌بندی *</label>
              <select v-model="form.category" class="select select-bordered w-full select-sm" required>
                <option value="">انتخاب کنید</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
            <div>
              <label class="label-text text-xs text-lumia-dark/60 block mb-1">برند</label>
              <select v-model="form.brand" class="select select-bordered w-full select-sm">
                <option value="">بدون برند</option>
                <option v-for="b in brands" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Images -->
        <div v-if="!isNew" class="bg-white rounded-2xl p-6 shadow-sm border border-base-200">
          <h3 class="font-bold text-lumia-dark mb-4 pb-3 border-b border-base-200">تصاویر محصول</h3>
          <div class="grid grid-cols-3 gap-2 mb-3">
            <div v-for="img in productImages" :key="img.id" class="relative group">
              <img :src="img.image" class="w-full aspect-square object-cover rounded-lg border border-base-200" />
              <button
                type="button"
                class="absolute top-1 left-1 w-5 h-5 bg-error text-white rounded-full text-xs items-center justify-center hidden group-hover:flex"
                @click="deleteImage(img.id)"
              >×</button>
            </div>
          </div>
          <AdminImageUpload label="افزودن تصویر" :multiple="true" @files="uploadImages" />
        </div>
      </div>
    </form>

    <div v-if="error" class="alert alert-error mt-4 text-sm">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ productId?: string; isNew?: boolean }>()
const { apiFetch } = useApi()
const router = useRouter()

const loading = ref(!props.isNew)
const saving = ref(false)
const error = ref('')
const categories = ref<any[]>([])
const brands = ref<any[]>([])
const productImages = ref<any[]>([])

const form = ref({
  name: '',
  slug: '',
  short_description: '',
  description: '',
  original_price: 0,
  discounted_price: 0,
  stock: 0,
  sku: '',
  is_active: true,
  is_featured: false,
  category: '' as string,
  brand: '' as string | null,
  meta_title: '',
  meta_description: '',
  attributes: [] as { key: string; value: string }[],
})

async function loadDropdowns() {
  const [cats, brs] = await Promise.all([
    apiFetch<any>('/admin/categories/'),
    apiFetch<any>('/admin/brands/'),
  ])
  categories.value = cats.results ?? cats
  brands.value = brs.results ?? brs
}

async function loadProduct() {
  const p = await apiFetch<any>(`/admin/products/${props.productId}/`)
  form.value = {
    name: p.name,
    slug: p.slug,
    short_description: p.short_description ?? '',
    description: p.description ?? '',
    original_price: p.compare_at_price ?? p.price,
    discounted_price: p.price,
    stock: p.stock,
    sku: p.sku ?? '',
    is_active: p.is_active,
    is_featured: p.is_featured,
    category: p.category,
    brand: p.brand ?? '',
    meta_title: p.meta_title ?? '',
    meta_description: p.meta_description ?? '',
    attributes: p.attributes ?? [],
  }
  productImages.value = p.images ?? []
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    const body = {
      ...form.value,
      brand: form.value.brand || null,
    }
    if (props.isNew) {
      const created = await apiFetch<any>('/admin/products/', { method: 'POST', body })
      router.push(`/admin/products/${created.id}`)
    } else {
      await apiFetch(`/admin/products/${props.productId}/`, { method: 'PATCH', body })
    }
  } catch (e: any) {
    error.value = e.data?.detail ?? JSON.stringify(e.data) ?? 'خطا در ذخیره'
  } finally {
    saving.value = false
  }
}

async function deleteProduct() {
  if (!confirm('آیا مطمئن هستید؟ این عملیات قابل بازگشت نیست.')) return
  await apiFetch(`/admin/products/${props.productId}/`, { method: 'DELETE' })
  router.push('/admin/products')
}

async function uploadImages(files: File[]) {
  const formData = new FormData()
  files.forEach(f => formData.append('images', f))
  const res = await apiFetch<any[]>(`/admin/products/${props.productId}/images/`, {
    method: 'POST',
    body: formData,
  })
  productImages.value.push(...res)
}

async function deleteImage(imgId: string) {
  await apiFetch(`/admin/products/${props.productId}/images/${imgId}/`, { method: 'DELETE' })
  productImages.value = productImages.value.filter(i => i.id !== imgId)
}

function addAttr() {
  form.value.attributes.push({ key: 'scent', value: '' })
}

function removeAttr(i: number) {
  form.value.attributes.splice(i, 1)
}

onMounted(async () => {
  await loadDropdowns()
  if (!props.isNew && props.productId) {
    await loadProduct()
  }
  loading.value = false
})
</script>
