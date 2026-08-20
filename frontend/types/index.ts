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

export interface AdminCategory {
  id: string
  name: string
  slug: string
  description?: string
  image?: string | null
  parent: string | null
  mood?: string
  is_active: boolean
  meta_title?: string
  meta_description?: string
  created_at?: string
  children?: { id: string; name: string; slug: string }[]
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
  purchase_code?: string
  status: string
  status_display: string
  subtotal: number
  discount_amount: number
  shipping_cost: number
  total: number
  coupon_code?: string
  free_shipping?: boolean
  shipping_name?: string
  shipping_phone?: string
  shipping_province?: string
  shipping_city?: string
  shipping_address?: string
  shipping_postal_code?: string
  shipping_plate_number?: string
  tracking_number?: string | null
  expires_at?: string | null
  note?: string
  payment_status?: string | null
  payment_status_display?: string
  items: OrderItem[]
  created_at: string
  updated_at?: string
}

export interface OrderItem {
  id: string
  product_name: string
  product_price: number
  quantity: number
  subtotal: number
  product?: string | null
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

export interface InstagramPage {
  id: string
  username: string
  label: string
  profile_url: string
  is_active?: boolean
  created_at?: string
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
  shipping_cost: number
  free_shipping_threshold: number
  contact_sms_phone?: string
  contact_telegram?: string
  contact_whatsapp?: string
  contact_bale?: string
}

export interface StoreContact {
  contact_sms_phone: string
  contact_telegram: string
  contact_whatsapp: string
  contact_bale: string
}

export interface ZarinpalSettings {
  merchant_id: string
  is_sandbox: boolean
  is_mock: boolean
  callback_url: string
  callback_url_resolved: string
  currency: 'IRR' | 'IRT'
  client_id: string
  client_secret_masked?: string
  terminal_id: string
  auto_reconcile: boolean
  max_retry_attempts: number
  enable_api_logging: boolean
  token_valid: boolean
  token_expires_at: string | null
  updated_at?: string
}

export interface PaymentDetail {
  authority: string
  ref_id: string
  card_pan: string
  fee: number | null
  paid_at: string | null
  error_code: number | null
  is_recent: boolean
}

export interface ShippingSettings {
  shipping_cost: number
  free_shipping_threshold: number
}

export interface AuthSettings {
  access_token_lifetime_minutes: number
  refresh_token_lifetime_days: number
  rotate_refresh_tokens: boolean
  admin_bypass_phone: string
}

export interface AdminNotificationsSummary {
  awaiting_payment: number
  pending_orders: number
  pending_reviews: number
  low_stock_count: number
}

export interface AdminDashboardStats {
  new_orders_count: number
  today_income: number
  weekly_income: number
  total_orders: number
  total_users: number
  total_products: number
  low_stock_count: number
  pending_reviews_count: number
  daily_revenue: { date: string; revenue: number; order_count: number }[]
  top_products: { id: string; name: string; slug: string; sales_count: number; stock: number; price: number }[]
  orders_by_status: Record<string, number>
  recent_orders: { id: string; order_number: string; user_phone: string; status: string; total: number; created_at: string }[]
}

export interface LowStockProduct {
  id: string
  name: string
  slug: string
  sku: string
  stock: number
  price: number
  category_name: string
  brand_name: string
  primary_image: string | null
}

export interface InventorySummary {
  out_of_stock: number
  low_stock: number
  healthy: number
  total: number
  default_threshold: number
}

export interface InventoryProduct extends LowStockProduct {
  stock_unit_label: string
  pack_label: string
  stock_pack_sizes: number[]
  low_stock_threshold: number | null
  effective_threshold: number
  effective_pack_sizes: number[]
  stock_status: 'out' | 'low' | 'ok'
}

export interface StockMovement {
  id: string
  product: string
  product_name: string
  delta: number
  stock_before: number
  stock_after: number
  pack_size: number | null
  pack_count: number | null
  reason: string
  note: string
  created_by_phone: string
  created_at: string
}

export interface StockAdjustPayload {
  product_id: string
  mode: 'pack' | 'delta' | 'set'
  pack_size?: number
  pack_count?: number
  delta?: number
  absolute_stock?: number
  note?: string
}

export interface InventorySummary {
  out_of_stock: number
  low_stock: number
  healthy: number
  total: number
  default_threshold: number
}

export interface InventoryProduct {
  id: string
  name: string
  slug: string
  sku: string
  stock: number
  price: number
  category_name: string
  brand_name: string
  primary_image?: string | null
  stock_unit_label: string
  pack_label: string
  stock_pack_sizes: number[]
  low_stock_threshold: number | null
  effective_threshold: number
  effective_pack_sizes: number[]
  stock_status: 'out' | 'low' | 'ok'
}

export interface StockMovement {
  id: string
  product: string
  product_name: string
  delta: number
  stock_before: number
  stock_after: number
  pack_size: number | null
  pack_count: number | null
  reason: string
  note: string
  created_by_phone: string
  created_at: string
}

export interface StockAdjustPayload {
  product_id: string
  mode: 'pack' | 'delta' | 'set'
  pack_size?: number
  pack_count?: number
  delta?: number
  absolute_stock?: number
  note?: string
  reason?: string
}

export interface AdminHomeHero {
  id: string
  headline: string
  subheadline?: string
  description?: string
  cta_text?: string
  cta_url?: string
  cta_secondary_text?: string
  cta_secondary_url?: string
  badge_text?: string
  is_active: boolean
  video_webm_url?: string | null
  video_poster_url?: string | null
  fallback_image_url?: string | null
  updated_at?: string
}

export interface AdminTrustBadge {
  id: string
  icon: string
  title: string
  description?: string
  is_active: boolean
  created_at?: string
}

