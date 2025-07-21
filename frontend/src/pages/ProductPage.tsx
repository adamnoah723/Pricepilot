import React from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getProductDetail, getSimilarProducts } from '../services/api'
import PriceTable from '../components/PriceTable'
import ProductCard from '../components/ProductCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import DataFreshnessIndicator from '../components/DataFreshnessIndicator'
import { ExternalLink, Star } from 'lucide-react'

export default function ProductPage() {
  const { productId } = useParams<{ productId: string }>()

  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => getProductDetail(productId!),
    enabled: !!productId,
  })

  const { data: similarProducts } = useQuery({
    queryKey: ['similar-products', productId],
    queryFn: () => getSimilarProducts(productId!),
    enabled: !!productId,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <ErrorMessage message="Product not found or failed to load." />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Product Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Product Image */}
            <div className="aspect-square bg-gray-100 rounded-xl flex items-center justify-center">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  className="max-w-full max-h-full object-contain rounded-xl"
                />
              ) : (
                <div className="text-gray-400">
                  <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              )}
            </div>

            {/* Product Info */}
            <div>
              <div className="mb-4">
                {product.brand && (
                  <span className="text-emerald-600 font-medium text-sm uppercase tracking-wide">
                    {product.brand}
                  </span>
                )}
                <h1 className="text-3xl font-bold text-gray-900 mt-2 mb-4">
                  {product.name}
                </h1>
              </div>

              {/* Best Price */}
              <div className="mb-6">
                <div className="flex items-baseline space-x-2">
                  <span className="text-3xl font-bold text-emerald-600">
                    ${Number(product.best_price).toFixed(2)}
                  </span>
                  <span className="text-gray-500">Best Price</span>
                </div>
              </div>

              {/* Popularity Score */}
              <div className="flex items-center space-x-2 mb-6">
                <Star className="w-5 h-5 text-yellow-400 fill-current" />
                <span className="text-gray-600">
                  Popularity Score: {product.popularity_score}
                </span>
              </div>

              {/* Description */}
              {product.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
                  <p className="text-gray-600">{product.description}</p>
                </div>
              )}

              {/* Specifications */}
              {product.specifications && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Specifications</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-600 whitespace-pre-wrap">
                      {JSON.stringify(product.specifications, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Price Comparison Table */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4 sm:mb-0">Price Comparison</h2>
            <DataFreshnessIndicator productId={productId} className="flex-shrink-0" />
          </div>
          <PriceTable priceComparisons={product.price_comparison} />
        </div>

        {/* Similar Products */}
        {similarProducts && similarProducts.length > 0 && (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Similar Products</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {similarProducts.map((similarProduct) => (
                <ProductCard key={similarProduct.id} product={similarProduct} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}