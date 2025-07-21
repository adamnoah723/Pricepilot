import React from 'react'
import { Link } from 'react-router-dom'
import { Product } from '../services/api'
import { Star, TrendingDown } from 'lucide-react'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  return (
    <Link to={`/product/${product.id}`} className="block">
      <div className="card group">
        <div className="card-content">
          {/* Product Image */}
          <div className="aspect-square bg-gray-100 rounded-xl mb-4 flex items-center justify-center overflow-hidden">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform duration-300"
              />
            ) : (
              <div className="text-gray-400">
                <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="space-y-2">
            {/* Brand */}
            {product.brand && (
              <div className="text-emerald-600 font-medium text-sm uppercase tracking-wide">
                {product.brand}
              </div>
            )}

            {/* Product Name */}
            <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 group-hover:text-emerald-600 transition-colors">
              {product.name}
            </h3>

            {/* Price and Best Deal Badge */}
            <div className="flex items-center justify-between">
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold text-gray-900">
                  ${Number(product.best_price).toFixed(2)}
                </span>
              </div>
              
              <div className="flex items-center space-x-1 bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full text-xs font-medium">
                <TrendingDown className="w-3 h-3" />
                <span>Best Deal</span>
              </div>
            </div>

            {/* Popularity Score */}
            <div className="flex items-center space-x-1 text-sm text-gray-500">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span>Popularity: {product.popularity_score}</span>
            </div>

            {/* Match Score (if available) */}
            {product.match_score && (
              <div className="text-xs text-gray-400">
                Match: {product.match_score}%
              </div>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}