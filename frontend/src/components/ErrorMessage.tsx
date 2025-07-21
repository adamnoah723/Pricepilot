import React from 'react'
import { AlertCircle } from 'lucide-react'

interface ErrorMessageProps {
  message: string
  className?: string
}

export default function ErrorMessage({ message, className = '' }: ErrorMessageProps) {
  return (
    <div className={`flex items-center justify-center p-8 ${className}`}>
      <div className="text-center">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Something went wrong</h3>
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  )
}