import React, { useState, useRef, useEffect } from 'react'
import { Search, X } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { searchAutocomplete } from '../services/api'

interface SearchBarProps {
  onSearch: (query: string) => void
  placeholder?: string
  className?: string
}

interface AutocompleteSuggestion {
  id?: string
  text: string
  type: 'product' | 'brand'
  brand?: string
}

export default function SearchBar({ 
  onSearch, 
  placeholder = "Search for laptops, headphones, speakers...",
  className = ""
}: SearchBarProps) {
  const [query, setQuery] = useState('')
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const suggestionsRef = useRef<HTMLDivElement>(null)

  // Fetch autocomplete suggestions
  const { data: suggestions = [] } = useQuery({
    queryKey: ['autocomplete', query],
    queryFn: () => searchAutocomplete(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query.trim())
      setIsOpen(false)
      inputRef.current?.blur()
    }
  }

  const handleSuggestionClick = (suggestion: AutocompleteSuggestion) => {
    setQuery(suggestion.text)
    onSearch(suggestion.text)
    setIsOpen(false)
    inputRef.current?.blur()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || suggestions.length === 0) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < suggestions.length - 1 ? prev + 1 : prev
        )
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1)
        break
      case 'Enter':
        e.preventDefault()
        if (selectedIndex >= 0) {
          handleSuggestionClick(suggestions[selectedIndex])
        } else {
          handleSubmit(e)
        }
        break
      case 'Escape':
        setIsOpen(false)
        setSelectedIndex(-1)
        inputRef.current?.blur()
        break
    }
  }

  const clearSearch = () => {
    setQuery('')
    setIsOpen(false)
    setSelectedIndex(-1)
    inputRef.current?.focus()
  }

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsOpen(false)
        setSelectedIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className={`relative w-full ${className}`}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setIsOpen(e.target.value.length >= 2)
              setSelectedIndex(-1)
            }}
            onFocus={() => setIsOpen(query.length >= 2)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="search-input pl-12 pr-12"
          />
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </form>

      {/* Autocomplete Suggestions */}
      {isOpen && suggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-2xl shadow-xl mt-2 max-h-80 overflow-y-auto z-50"
        >
          {suggestions.map((suggestion, index) => (
            <button
              key={`${suggestion.type}-${suggestion.text}-${index}`}
              onClick={() => handleSuggestionClick(suggestion)}
              className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 transition-colors ${
                index === selectedIndex ? 'bg-emerald-50 border-l-4 border-emerald-500' : ''
              } ${index === 0 ? 'rounded-t-2xl' : ''} ${
                index === suggestions.length - 1 ? 'rounded-b-2xl' : ''
              }`}
            >
              <Search className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="text-gray-900 truncate">{suggestion.text}</div>
                {suggestion.brand && (
                  <div className="text-sm text-gray-500">{suggestion.brand}</div>
                )}
              </div>
              <div className="text-xs text-gray-400 capitalize">
                {suggestion.type}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}