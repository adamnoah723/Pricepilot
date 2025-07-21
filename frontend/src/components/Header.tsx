import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Menu, X } from 'lucide-react'
import SearchBar from './SearchBar'

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const navigate = useNavigate()

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <header className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <Search className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">PricePilot</span>
          </Link>

          {/* Desktop Search Bar */}
          <div className="hidden md:flex flex-1 max-w-lg mx-8">
            <SearchBar onSearch={handleSearch} />
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/category/laptops" 
              className="text-gray-700 hover:text-emerald-600 font-medium transition-colors"
            >
              Laptops
            </Link>
            <Link 
              to="/category/headphones" 
              className="text-gray-700 hover:text-emerald-600 font-medium transition-colors"
            >
              Headphones
            </Link>
            <Link 
              to="/category/speakers" 
              className="text-gray-700 hover:text-emerald-600 font-medium transition-colors"
            >
              Speakers
            </Link>
          </nav>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-md text-gray-700 hover:text-emerald-600"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Search Bar */}
        <div className="md:hidden pb-4">
          <SearchBar onSearch={handleSearch} />
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200">
          <div className="px-4 py-2 space-y-1">
            <Link
              to="/category/laptops"
              className="block px-3 py-2 text-gray-700 hover:text-emerald-600 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Laptops
            </Link>
            <Link
              to="/category/headphones"
              className="block px-3 py-2 text-gray-700 hover:text-emerald-600 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Headphones
            </Link>
            <Link
              to="/category/speakers"
              className="block px-3 py-2 text-gray-700 hover:text-emerald-600 font-medium"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Speakers
            </Link>
          </div>
        </div>
      )}
    </header>
  )
}