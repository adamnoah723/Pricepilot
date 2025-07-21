# PricePilot Frontend

A React + TypeScript frontend for the PricePilot price comparison application.

## Features

- 🔍 Product search with autocomplete
- 📊 Price comparison tables
- 📱 Responsive design with Tailwind CSS
- ⚡ Fast development with Vite
- 🎯 Type-safe with TypeScript
- 🔄 Data fetching with React Query

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **React Router** - Client-side routing
- **React Query** - Data fetching and caching
- **Lucide React** - Icons
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Update the API URL in `.env` if needed:
```
VITE_API_URL=http://localhost:8001
```

### Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3001`

### Building

Build for production:
```bash
npm run build
```

### Testing

Run tests:
```bash
npm run test
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ErrorMessage.tsx
│   ├── Footer.tsx
│   ├── Header.tsx
│   ├── Layout.tsx
│   ├── LoadingSpinner.tsx
│   ├── PriceTable.tsx
│   ├── ProductCard.tsx
│   └── SearchBar.tsx
├── pages/              # Page components
│   ├── CategoryPage.tsx
│   ├── HomePage.tsx
│   ├── ProductPage.tsx
│   └── SearchPage.tsx
├── services/           # API services
│   └── api.ts
├── App.tsx            # Main app component
├── main.tsx           # App entry point
└── index.css          # Global styles
```

## API Integration

The frontend communicates with the backend API running on port 8001. Key endpoints:

- `GET /api/products` - Get products
- `GET /api/search` - Search products
- `GET /api/categories` - Get categories
- `GET /api/vendors` - Get vendors
- `GET /api/products/:id` - Get product details
- `GET /api/autocomplete` - Search autocomplete

## Environment Variables

- `VITE_API_URL` - Backend API URL (default: http://localhost:8001)

## Styling

The app uses Tailwind CSS with custom components defined in `index.css`:

- `.btn` - Button styles
- `.card` - Card container styles
- `.search-input` - Search input styles

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new components
3. Use React Query for data fetching
4. Follow the component structure patterns