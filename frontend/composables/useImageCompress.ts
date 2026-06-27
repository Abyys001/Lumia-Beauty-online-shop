const MAX_WIDTH = 1200
const MAX_BYTES = 5 * 1024 * 1024
const WEBP_QUALITY = 0.85

function loadImage(file: File): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(file)
    img.onload = () => {
      URL.revokeObjectURL(url)
      resolve(img)
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('بارگذاری تصویر ناموفق بود'))
    }
    img.src = url
  })
}

function canvasToBlob(canvas: HTMLCanvasElement, type: string, quality: number): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('فشرده‌سازی تصویر ناموفق بود'))),
      type,
      quality,
    )
  })
}

function scaledDimensions(width: number, height: number, maxWidth: number) {
  if (width <= maxWidth) {
    return { width, height }
  }
  const ratio = maxWidth / width
  return { width: maxWidth, height: Math.round(height * ratio) }
}

export async function compressImageFile(file: File): Promise<File> {
  if (!file.type.startsWith('image/')) {
    throw new Error('فقط فایل تصویری مجاز است')
  }

  if (file.type === 'image/webp' && file.size <= MAX_BYTES) {
    const img = await loadImage(file)
    if (img.width <= MAX_WIDTH) {
      return file
    }
  }

  const img = await loadImage(file)
  const { width, height } = scaledDimensions(img.naturalWidth, img.naturalHeight, MAX_WIDTH)
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error('پردازش تصویر در مرورگر پشتیبانی نمی‌شود')
  }
  ctx.drawImage(img, 0, 0, width, height)

  const blob = await canvasToBlob(canvas, 'image/webp', WEBP_QUALITY)
  if (blob.size > MAX_BYTES) {
    throw new Error('حجم تصویر پس از فشرده‌سازی بیش از ۵ مگابایت است')
  }

  const baseName = file.name.replace(/\.[^.]+$/, '') || 'image'
  return new File([blob], `${baseName}.webp`, { type: 'image/webp', lastModified: Date.now() })
}

export async function compressImageFiles(files: File[]): Promise<File[]> {
  return Promise.all(files.map((file) => compressImageFile(file)))
}

export function useImageCompress() {
  return { compressImageFile, compressImageFiles }
}
