import React from 'react'
import { useNavigate } from 'react-router-dom'
import SearchBar from '../components/SearchBar'

export default function HomePage() {
  const navigate = useNavigate()

  const handleSearch = (query: string) => {
    navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50">
      {/* Hero Section */}
      <section className="pt-20 pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Find the Best
            <span className="text-emerald-500 block">Tech Deals</span>
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Compare prices across multiple vendors for laptops, headphones, and speakers.
            Save money and make informed purchasing decisions.
          </p>

          {/* Search Bar */}
          <div className="max-w-2xl mx-auto mb-16">
            <SearchBar
              onSearch={handleSearch}
              placeholder="Search for MacBook Pro, AirPods, JBL speakers..."
              className="text-lg"
            />
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Shop by Category
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Laptops */}
            <div
              className="card cursor-pointer group h-64"
              onClick={() => navigate('/category/laptops')}
            >
              <div className="card-content h-full flex flex-col justify-center text-center">
                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-emerald-200 transition-all duration-300 group-hover:scale-110">
                  <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-emerald-600 transition-colors">Laptops</h3>
                <p className="text-gray-600 text-lg">MacBooks, gaming laptops, ultrabooks and more</p>
                <div className="mt-4 text-emerald-600 font-medium group-hover:underline">
                  Browse Laptops →
                </div>
              </div>
            </div>

            {/* Headphones */}
            <div
              className="card cursor-pointer group h-64"
              onClick={() => navigate('/category/headphones')}
            >
              <div className="card-content h-full flex flex-col justify-center text-center">
                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-emerald-200 transition-all duration-300 group-hover:scale-110">
                  <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-emerald-600 transition-colors">Headphones</h3>
                <p className="text-gray-600 text-lg">AirPods, noise-canceling, gaming headsets</p>
                <div className="mt-4 text-emerald-600 font-medium group-hover:underline">
                  Browse Headphones →
                </div>
              </div>
            </div>

            {/* Speakers */}
            <div
              className="card cursor-pointer group h-64"
              onClick={() => navigate('/category/speakers')}
            >
              <div className="card-content h-full flex flex-col justify-center text-center">
                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6 group-hover:bg-emerald-200 transition-all duration-300 group-hover:scale-110">
                  <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-emerald-600 transition-colors">Speakers</h3>
                <p className="text-gray-600 text-lg">Bluetooth speakers, soundbars, smart speakers</p>
                <div className="mt-4 text-emerald-600 font-medium group-hover:underline">
                  Browse Speakers →
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Best Deals Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            Today's Best Deals
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Deal Card 1 */}
            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded-full">
                    25% OFF
                  </span>
                  <span className="text-sm text-gray-500">Amazon</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  MacBook Pro 14" M3
                </h3>
                <div className="flex items-baseline space-x-2 mb-4">
                  <span className="text-2xl font-bold text-emerald-600">$1,499</span>
                  <span className="text-lg text-gray-500 line-through">$1,999</span>
                </div>
                <p className="text-gray-600 text-sm mb-4">
                  Professional laptop with M3 chip, perfect for developers and creators.
                </p>
                <button
                  className="btn btn-primary w-full"
                  onClick={() => navigate('/search?q=MacBook+Pro+14')}
                >
                  View Deal
                </button>
              </div>
            </div>

            {/* Deal Card 2 */}
            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded-full">
                    30% OFF
                  </span>
                  <span className="text-sm text-gray-500">Best Buy</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Sony WH-1000XM4
                </h3>
                <div className="flex items-baseline space-x-2 mb-4">
                  <span className="text-2xl font-bold text-emerald-600">$248</span>
                  <span className="text-lg text-gray-500 line-through">$349</span>
                </div>
                <p className="text-gray-600 text-sm mb-4">
                  Industry-leading noise canceling headphones with 30-hour battery.
                </p>
                <button
                  className="btn btn-primary w-full"
                  onClick={() => navigate('/search?q=Sony+WH-1000XM4')}
                >
                  View Deal
                </button>
              </div>
            </div>

            {/* Deal Card 3 */}
            <div className="card">
              <div className="card-content">
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-red-100 text-red-800 text-xs font-bold px-2 py-1 rounded-full">
                    20% OFF
                  </span>
                  <span className="text-sm text-gray-500">Walmart</span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  JBL Charge 5
                </h3>
                <div className="flex items-baseline space-x-2 mb-4">
                  <span className="text-2xl font-bold text-emerald-600">$119</span>
                  <span className="text-lg text-gray-500 line-through">$149</span>
                </div>
                <p className="text-gray-600 text-sm mb-4">
                  Portable Bluetooth speaker with powerful sound and 20-hour playtime.
                </p>
                <button
                  className="btn btn-primary w-full"
                  onClick={() => navigate('/search?q=JBL+Charge+5')}
                >
                  View Deal
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">
            How It Works
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-3xl font-bold text-white">1</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Search</h3>
              <p className="text-gray-600 text-lg">
                Search for the tech product you want to buy using our smart search
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-3xl font-bold text-white">2</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Compare</h3>
              <p className="text-gray-600 text-lg">
                View prices from multiple vendors side by side with real-time updates
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <span className="text-3xl font-bold text-white">3</span>
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">Save</h3>
              <p className="text-gray-600 text-lg">
                Buy from the vendor with the best deal and save money
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Vendor Logos Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
            We Compare Prices From
          </h2>

          <div className="flex justify-center items-center space-x-12 opacity-60">
            <div className="text-2xl font-bold text-gray-800">Amazon</div>
            <div className="text-2xl font-bold text-gray-800">Best Buy</div>
            <div className="text-2xl font-bold text-gray-800">Walmart</div>
            <div className="text-2xl font-bold text-gray-800">+ More</div>
          </div>
        </div>
      </section>
    </div>
  )
}