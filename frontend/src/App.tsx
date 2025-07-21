import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import SearchPage from './pages/SearchPage'
import CategoryPage from './pages/CategoryPage'
import ProductPage from './pages/ProductPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/category/:categoryId" element={<CategoryPage />} />
        <Route path="/product/:productId" element={<ProductPage />} />
      </Routes>
    </Layout>
  )
}

export default App