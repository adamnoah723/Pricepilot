import React, { useState } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProducts, getCategories } from '../services/api'
import ProductCard from '../components/ProductCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function CategoryPage() {
  const { categoryId } = useParams<{ categoryId: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const [sortBy, setSortBy] = useState(searchParams.get('sort') || 'popularity')

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
  })

  const { data, isLoading, error } = useQuery({
    queryKey: ['products', categoryId, sortBy],
    queryFn: () => getProducts(categoryId, sortBy),
    enabled: !!categoryId,
  })

  const category = categories?.find(cat => cat.name === categoryId)

  const handleSortChange = (newSortBy: string) => {
    setSortBy(newSortBy)
    setSearchParams({ sort: newSortBy })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <ErrorMessage message="Failed to load products. Please try again." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {category?.display_name || categoryId}
          </h1>
          <p className="text-gray-600">
            {data?.total || 0} products available
          </p>
        </div>

        {/* Filters and Sorting */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 space-y-4 sm:space-y-0">
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => handleSortChange(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="popularity">Most Popular</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
              <option value="name">Name: A to Z</option>
            </select>
          </div>
        </div>

        {/* Products Grid */}
        {data?.products && data.products.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {data.products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No products found</h3>
            <p className="text-gray-600">Check back later for new products in this category.</p>
          </div>
        )}
      </div>
    </div>
  )
}