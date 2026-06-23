export interface Product {
  id: string
  name: string
  name_en?: string
  slug: string
  short_description: string
  description?: string
  price: number
  compare_at_price: number | null
  discount_percent: number
  stock: number
  is_in_stock: boolean
  is_featured: boolean
  primary_image: string | null
  brand_name: string
  category_name: string
  sales_count: number
  images?: ProductImage[]
  attributes?: ProductAttribute[]
  reviews?: Review[]
  average_rating?: number | null
  meta_title?: string
  meta_description?: string
  license_holder?: string
  brand?: Brand
  category?: Category
}

export interface ProductImage {
  id: string
  image: string
  alt_text: string
  is_primary: boolean
}

export interface ProductAttribute {
  key: string
  key_display: string
  value: string
}

export interface Review {
  id: string
  user_name: string
  rating: number
  comment: string
  image?: string | null
  created_at: string
}

export interface Category {
  id: string
  name: string
  slug: string
  description: string
  image: string | null
  mood: string
  children: Category[]
}

export interface CartItem {
  id: string
  product: Product
  quantity: number
  subtotal: number
}

export interface Cart {
  id: string
  items: CartItem[]
  total: number
  item_count: number
}

export interface User {
  id: string
  phone: string
  first_name: string
  last_name: string
  full_name: string
  email: string
  is_staff?: boolean
}

export interface Address {
  id: string
  title: string
  province: string
  city: string
  address_line: string
  postal_code: string
  receiver_name: string
  receiver_phone: string
  is_default: boolean
}

export interface Order {
  id: string
  order_number: string
  status: string
  status_display: string
  subtotal: number
  discount_amount: number
  shipping_cost: number
  total: number
  items: OrderItem[]
  created_at: string
}

export interface OrderItem {
  id: string
  product_name: string
  product_price: number
  quantity: number
  subtotal: number
}

export interface BlogPost {
  id: string
  title: string
  slug: string
  excerpt: string
  content?: string
  cover_image: string | null
  published_at: string
  is_featured?: boolean
  meta_title?: string
  meta_description?: string
  category?: { name: string; slug: string }
}

export interface InstagramPost {
  id: string
  image: string
  post_url: string
  caption: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface HomeHero {
  headline: string
  subheadline?: string
  description?: string
  cta_text?: string
  cta_url?: string
  cta_secondary_text?: string
  cta_secondary_url?: string
  badge_text?: string
  video_webm_url?: string | null
  video_poster_url?: string | null
  fallback_image_url?: string | null
}

export interface TrustBadge {
  icon: string
  title: string
  description?: string
  sort_order?: number
}

export interface HomeCMS {
  hero: HomeHero | null
  trust_badges: TrustBadge[]
}

export interface Brand {
  id: string
  name: string
  slug: string
  logo?: string | null
}

export interface StoreSettings {
  zarinpal_merchant_id: string
}

export interface SmsProviderSettings {
  provider_mode: 'mock' | 'smsir'
  api_key?: string
  base_url: string
  is_sandbox: boolean
  is_active: boolean
  last_test_at: string | null
  last_test_status: string
  last_test_message: string
  updated_at?: string
}

export interface SmsProviderStatus {
  provider_mode: string
  is_active: boolean
  is_sandbox: boolean
  has_api_key: boolean
  last_test_at: string | null
  last_test_status: string
  last_test_message: string
  credit: number | null
  runtime_provider: string
}

export interface OtpTemplate {
  id: string
  name: string
  sms_ir_template_id: number
  parameter_name: string
  body_preview: string
  is_active: boolean
  is_default: boolean
  created_at?: string
  updated_at?: string
}

export interface OtpSettings {
  otp_length: number
  expiry_seconds: number
  max_verify_attempts: number
  verify_window_seconds: number
  rate_limit_count: number
  rate_limit_window_seconds: number
  resend_delay_seconds: number
  ip_rate_limit_count: number
  ip_rate_limit_window_seconds: number
}

export interface AuthSettings {
  otp_login_enabled: boolean
  access_token_lifetime_minutes: number
  refresh_token_lifetime_days: number
  rotate_refresh_tokens: boolean
  admin_bypass_phone: string
}

export interface SmsLog {
  id: string
  phone: string
  message_type: string
  template: string | null
  template_name?: string
  provider: string
  status: string
  request_data: Record<string, unknown>
  response_data: Record<string, unknown>
  provider_message_id: string
  error_message: string
  ip_address: string | null
  created_at: string
}

