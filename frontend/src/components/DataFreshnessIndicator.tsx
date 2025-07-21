import React, { useState, useEffect } from 'react'
import { Clock, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react'

interface FreshnessData {
  vendor_name: string
  last_updated: string
  hours_old: number
  freshness_status: 'fresh' | 'aging' | 'stale'
  product_id?: string
}

interface DataFreshnessProps {
  productId?: string
  className?: string
}

export default function DataFreshnessIndicator({ productId, className = '' }: DataFreshnessProps) {
  const [freshnessData, setFreshnessData] = useState<{
    vendor_data: FreshnessData[]
    statistics: {
      average_age_hours: number
      oldest_data_hours: number
      newest_data_hours: number
      total_vendors: number
    }
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchFreshnessData()
  }, [productId])

  const fetchFreshnessData = async () => {
    try {
      setLoading(true)
      const url = productId 
        ? `/api/data-freshness?product_id=${productId}`
        : '/api/data-freshness'
      
      const response = await fetch(`http://localhost:8000${url}`)
      if (!response.ok) {
        throw new Error('Failed to fetch freshness data')
      }
      
      const data = await response.json()
      if (data.error) {
        setError(data.error)
      } else {
        setFreshnessData(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const formatTimeAgo = (hoursOld: number): string => {
    if (hoursOld < 1) {
      const minutes = Math.round(hoursOld * 60)
      return `${minutes}m ago`
    } else if (hoursOld < 24) {
      return `${Math.round(hoursOld)}h ago`
    } else {
      const days = Math.round(hoursOld / 24)
      return `${days}d ago`
    }
  }

  const getFreshnessIcon = (status: string) => {
    switch (status) {
      case 'fresh':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'aging':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'stale':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getFreshnessColor = (status: string) => {
    switch (status) {
      case 'fresh':
        return 'text-green-600 bg-green-50 border-green-200'
      case 'aging':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'stale':
        return 'text-red-600 bg-red-50 border-red-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className={`flex items-center space-x-2 text-gray-500 ${className}`}>
        <RefreshCw className="w-4 h-4 animate-spin" />
        <span className="text-sm">Checking data freshness...</span>
      </div>
    )
  }

  if (error || !freshnessData) {
    return (
      <div className={`flex items-center space-x-2 text-red-500 ${className}`}>
        <AlertCircle className="w-4 h-4" />
        <span className="text-sm">Unable to check data freshness</span>
      </div>
    )
  }

  const { vendor_data, statistics } = freshnessData

  // For single product view, show individual vendor freshness
  if (productId && vendor_data.length > 0) {
    return (
      <div className={`space-y-2 ${className}`}>
        <div className="text-sm font-medium text-gray-700 mb-2">Price Data Freshness</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
          {vendor_data.map((vendor) => (
            <div
              key={vendor.vendor_name}
              className={`flex items-center justify-between px-3 py-2 rounded-lg border text-sm ${getFreshnessColor(vendor.freshness_status)}`}
            >
              <div className="flex items-center space-x-2">
                {getFreshnessIcon(vendor.freshness_status)}
                <span className="font-medium">{vendor.vendor_name}</span>
              </div>
              <span className="text-xs">
                {formatTimeAgo(vendor.hours_old)}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // For general view, show overall statistics
  return (
    <div className={`flex items-center space-x-4 ${className}`}>
      <div className="flex items-center space-x-2">
        <Clock className="w-4 h-4 text-gray-500" />
        <span className="text-sm text-gray-600">
          Data updated {formatTimeAgo(statistics.average_age_hours)} on average
        </span>
      </div>
      
      <button
        onClick={fetchFreshnessData}
        className="flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-800 transition-colors"
      >
        <RefreshCw className="w-4 h-4" />
        <span>Refresh</span>
      </button>
      
      <div className="text-xs text-gray-500">
        {statistics.total_vendors} vendors tracked
      </div>
    </div>
  )
}

// Utility component for showing time ago in a more readable format
export function TimeAgo({ timestamp, className = '' }: { timestamp: string, className?: string }) {
  const [timeAgo, setTimeAgo] = useState('')

  useEffect(() => {
    const updateTimeAgo = () => {
      const now = new Date()
      const past = new Date(timestamp)
      const diffMs = now.getTime() - past.getTime()
      const diffHours = diffMs / (1000 * 60 * 60)

      if (diffHours < 1) {
        const minutes = Math.round(diffMs / (1000 * 60))
        setTimeAgo(`${minutes}m ago`)
      } else if (diffHours < 24) {
        setTimeAgo(`${Math.round(diffHours)}h ago`)
      } else {
        const days = Math.round(diffHours / 24)
        setTimeAgo(`${days}d ago`)
      }
    }

    updateTimeAgo()
    const interval = setInterval(updateTimeAgo, 60000) // Update every minute

    return () => clearInterval(interval)
  }, [timestamp])

  return (
    <span className={`text-sm text-gray-500 ${className}`} title={new Date(timestamp).toLocaleString()}>
      {timeAgo}
    </span>
  )
}