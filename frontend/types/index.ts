export interface Product {
  id: string
  name: string
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
  meta_title?: string
  meta_description?: string
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
