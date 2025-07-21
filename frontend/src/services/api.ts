import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
})

// Types
export interface Category {
  id: string
  name: string
  display_name: string
}

export interface Vendor {
  id: string
  name: string
  display_name: string
  base_url?: string
  logo_url?: string
}

export interface Product {
  id: string
  name: string
  brand?: string
  category_id?: string
  image_url?: string
  best_price: number
  best_vendor_id: string
  popularity_score: number
  match_score?: number
}

export interface PriceComparison {
  vendor_id: string
  vendor_name: string
  vendor_logo_url?: string
  price: number
  original_price?: number
  discount_percentage?: number
  stock_status: string
  product_url: string
  is_best_deal: boolean
  last_updated?: string
}

export interface ProductDetail {
  id: string
  name: string
  brand?: string
  category_id?: string
  image_url?: string
  description?: string
  specifications?: Record<string, any>
  price_comparison: PriceComparison[]
  best_price: number
  best_vendor_id: string
  popularity_score: number
}

export interface SearchResponse {
  products: Product[]
  total: number
  limit: number
  offset: number
}

export interface AutocompleteSuggestion {
  id?: string
  text: string
  type: 'product' | 'brand'
  brand?: string
}

export interface ScraperStatus {
  vendor_id: string
  vendor_name: string
  status: string
  last_run_at?: string
  products_scraped: number
  errors_count: number
  duration_seconds?: number
}

// API Functions
export const getCategories = async (): Promise<Category[]> => {
  const response = await api.get('/api/categories')
  return response.data
}

export const getVendors = async (): Promise<Vendor[]> => {
  const response = await api.get('/api/vendors')
  return response.data
}

export const searchProducts = async (
  query: string,
  categoryId?: string,
  limit = 20,
  offset = 0
): Promise<SearchResponse> => {
  const params = new URLSearchParams({
    q: query,
    limit: limit.toString(),
    offset: offset.toString(),
  })
  
  if (categoryId) {
    params.append('category_id', categoryId)
  }
  
  const response = await api.get(`/api/search?${params}`)
  return response.data
}

export const getProducts = async (
  categoryId?: string,
  sortBy = 'popularity',
  limit = 20,
  offset = 0
): Promise<SearchResponse> => {
  const params = new URLSearchParams({
    sort_by: sortBy,
    limit: limit.toString(),
    offset: offset.toString(),
  })
  
  if (categoryId) {
    params.append('category_id', categoryId)
  }
  
  const response = await api.get(`/api/products?${params}`)
  return response.data
}

export const getProductDetail = async (productId: string): Promise<ProductDetail> => {
  const response = await api.get(`/api/products/${productId}`)
  return response.data
}

export const getSimilarProducts = async (
  productId: string,
  limit = 4
): Promise<Product[]> => {
  const response = await api.get(`/api/products/${productId}/similar?limit=${limit}`)
  return response.data
}

export const searchAutocomplete = async (query: string): Promise<AutocompleteSuggestion[]> => {
  if (query.length < 2) return []
  
  const response = await api.get(`/api/autocomplete?q=${encodeURIComponent(query)}`)
  return response.data.suggestions || []
}

export const getScraperStatus = async (): Promise<ScraperStatus[]> => {
  const response = await api.get('/api/scraper-status')
  return response.data
}

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 404) {
      throw new Error('Resource not found')
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.')
    }
    throw error
  }
)