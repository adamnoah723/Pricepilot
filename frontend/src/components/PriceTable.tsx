import React from 'react'
import { PriceComparison } from '../services/api'
import { ExternalLink, CheckCircle, XCircle, Clock } from 'lucide-react'
import { TimeAgo } from './DataFreshnessIndicator'

interface PriceTableProps {
  priceComparisons: PriceComparison[]
}

export default function PriceTable({ priceComparisons }: PriceTableProps) {
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getStockIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_stock':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'out_of_stock':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'limited_stock':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'unavailable':
        return <XCircle className="w-5 h-5 text-gray-500" />
      case 'discontinued':
        return <XCircle className="w-5 h-5 text-gray-400" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStockText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_stock':
        return 'In Stock'
      case 'out_of_stock':
        return 'Out of Stock'
      case 'limited_stock':
        return 'Limited Stock'
      case 'unavailable':
        return 'Unavailable'
      case 'discontinued':
        return 'Discontinued'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Vendor</th>
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Price</th>
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Discount</th>
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Stock</th>
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Last Updated</th>
            <th className="text-left py-4 px-4 font-semibold text-gray-900">Action</th>
          </tr>
        </thead>
        <tbody>
          {priceComparisons.map((comparison) => (
            <tr
              key={comparison.vendor_id}
              className={`border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                comparison.is_best_deal ? 'bg-emerald-50 border-emerald-200' : ''
              }`}
            >
              {/* Vendor */}
              <td className="py-4 px-4">
                <div className="flex items-center space-x-3">
                  {comparison.vendor_logo_url && (
                    <img
                      src={comparison.vendor_logo_url}
                      alt={comparison.vendor_name}
                      className="w-8 h-8 object-contain"
                    />
                  )}
                  <div>
                    <div className="font-medium text-gray-900">
                      {comparison.vendor_name}
                    </div>
                    {comparison.is_best_deal && (
                      <div className="text-xs text-emerald-600 font-medium">
                        Best Deal
                      </div>
                    )}
                  </div>
                </div>
              </td>

              {/* Price */}
              <td className="py-4 px-4">
                <div className="space-y-1">
                  <div className={`text-lg font-bold ${
                    comparison.is_best_deal ? 'text-emerald-600' : 'text-gray-900'
                  }`}>
                    ${Number(comparison.price).toFixed(2)}
                  </div>
                  {comparison.original_price && comparison.original_price > comparison.price && (
                    <div className="text-sm text-gray-500 line-through">
                      ${Number(comparison.original_price).toFixed(2)}
                    </div>
                  )}
                </div>
              </td>

              {/* Discount */}
              <td className="py-4 px-4">
                {comparison.discount_percentage && comparison.discount_percentage > 0 ? (
                  <div className="inline-flex items-center px-2 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                    -{Number(comparison.discount_percentage).toFixed(0)}%
                  </div>
                ) : (
                  <span className="text-gray-400">-</span>
                )}
              </td>

              {/* Stock Status */}
              <td className="py-4 px-4">
                <div className="flex items-center space-x-2">
                  {getStockIcon(comparison.stock_status)}
                  <span className={`text-sm font-medium ${
                    comparison.stock_status.toLowerCase() === 'in_stock' 
                      ? 'text-green-700' 
                      : comparison.stock_status.toLowerCase() === 'out_of_stock'
                      ? 'text-red-700'
                      : comparison.stock_status.toLowerCase() === 'limited_stock'
                      ? 'text-yellow-700'
                      : comparison.stock_status.toLowerCase() === 'unavailable'
                      ? 'text-gray-600'
                      : comparison.stock_status.toLowerCase() === 'discontinued'
                      ? 'text-gray-500'
                      : 'text-gray-600'
                  }`}>
                    {getStockText(comparison.stock_status)}
                  </span>
                </div>
              </td>

              {/* Last Updated */}
              <td className="py-4 px-4">
                {comparison.last_updated ? (
                  <TimeAgo timestamp={comparison.last_updated} />
                ) : (
                  <span className="text-sm text-gray-500">Unknown</span>
                )}
              </td>

              {/* Action */}
              <td className="py-4 px-4">
                <a
                  href={comparison.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    comparison.is_best_deal
                      ? 'bg-emerald-500 text-white hover:bg-emerald-600 shadow-lg hover:shadow-xl'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  } ${['out_of_stock', 'unavailable', 'discontinued'].includes(comparison.stock_status.toLowerCase()) ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
                  onClick={(e: React.MouseEvent<HTMLAnchorElement>) => {
                    if (['out_of_stock', 'unavailable', 'discontinued'].includes(comparison.stock_status.toLowerCase())) {
                      e.preventDefault()
                    }
                  }}
                >
                  <span>
                    {comparison.stock_status.toLowerCase() === 'out_of_stock' ? 'Out of Stock' :
                     comparison.stock_status.toLowerCase() === 'unavailable' ? 'Unavailable' :
                     comparison.stock_status.toLowerCase() === 'discontinued' ? 'Discontinued' :
                     comparison.stock_status.toLowerCase() === 'limited_stock' ? 'Limited Stock' :
                     'View Deal'}
                  </span>
                  {!['out_of_stock', 'unavailable', 'discontinued'].includes(comparison.stock_status.toLowerCase()) && (
                    <ExternalLink className="w-4 h-4" />
                  )}
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}