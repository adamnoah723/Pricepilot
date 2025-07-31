# PricePilot 🚀

A modern, hyper-fast price comparison platform for high-ticket tech items. Compare prices instantly across Amazon, Best Buy, Walmart, and brand websites with real-time data and smart search.

![PricePilot Demo](https://via.placeholder.com/800x400/10B981/FFFFFF?text=PricePilot+Price+Comparison)

## ✨ Features

- 🔍 **Smart Search**: Fuzzy matching and autocomplete for easy product discovery
- 💰 **Real-time Price Comparison**: Live prices from 4+ major retailers
- 🎯 **Best Deal Highlighting**: Instantly spot the lowest prices and biggest discounts
- 📱 **Responsive Design**: Beautiful, modern UI that works on all devices
- 🤖 **Automated Data Collection**: Web scrapers keep price data fresh
- ⚡ **Lightning Fast**: Optimized for speed with modern tech stack

## 🛍️ Supported Retailers

- **Amazon** - Real-time scraping with stealth capabilities
- **Best Buy** - Product links and pricing data
- **Walmart** - Price comparisons and stock status
- **Brand Websites** - Direct from manufacturer pricing

## 🚀 Quick Start

**Get PricePilot running in under 2 minutes:**

```bash
# Clone the repository
git clone https://github.com/adamnoah723/Pricepilot.git
cd Pricepilot

# Start with Docker (recommended)
docker-compose up --build

# Populate with sample data
docker-compose exec backend python run_scrapers.py
```

**Access the application:**
- 🌐 **Frontend**: http://localhost:3001
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

**That's it!** 🎉 Start comparing prices immediately.

## 📋 Detailed Setup

For manual installation, custom configuration, or development setup, see our comprehensive [**SETUP.md**](SETUP.md) guide.

## 🏗️ Tech Stack

**Frontend**
- React 18 + TypeScript
- TailwindCSS for styling
- Vite for blazing-fast builds
- React Query for data fetching

**Backend**
- FastAPI for high-performance APIs
- SQLAlchemy ORM with PostgreSQL/SQLite
- Async request handling
- Comprehensive error handling

**Scrapers**
- Python with async/await
- Selenium for dynamic content
- BeautifulSoup for HTML parsing
- Smart retry logic and rate limiting

**DevOps**
- Docker & Docker Compose
- Automated CI/CD ready
- Environment-based configuration

## 🎯 How It Works

1. **Search**: Enter any tech product (MacBook, headphones, etc.)
2. **Compare**: See prices from all major retailers instantly
3. **Save**: Click "View Deal" to go directly to the best price
4. **Stay Updated**: Prices refresh automatically via background scrapers

## 📊 Project Structure

```
PricePilot/
├── 🎨 frontend/          # React TypeScript app
│   ├── src/components/   # Reusable UI components
│   ├── src/pages/        # Page components
│   └── src/services/     # API integration
├── ⚙️ backend/           # FastAPI server
│   ├── app/             # Core application logic
│   ├── alembic/         # Database migrations
│   └── run_scrapers.py  # Scraper orchestration
├── 🕷️ scrapers/          # Web scraping modules
│   ├── amazon_scraper.py # Amazon integration
│   ├── bestbuy_scraper.py # Best Buy integration
│   └── base.py          # Scraper base classes
├── 🐳 docker-compose.yml # Multi-service orchestration
└── 📋 SETUP.md          # Detailed setup guide
```

## 🔧 Configuration

**Environment Variables:**
- `VITE_API_URL`: Frontend API endpoint
- `DATABASE_URL`: Database connection string
- `SCRAPER_HEADLESS`: Run scrapers in headless mode
- `*_RATE_LIMIT`: Rate limiting for each vendor

**Customization:**
- Add new retailers by extending `BaseScraper`
- Modify UI themes in `tailwind.config.js`
- Configure scraping intervals in `backend/scheduler.py`

## 🤝 Contributing

We welcome contributions! This project follows spec-driven development:

1. 📋 **Requirements**: See `.kiro/specs/price-pilot/requirements.md`
2. 🎨 **Design**: Architecture in `.kiro/specs/price-pilot/design.md`
3. ✅ **Tasks**: Implementation plan in `.kiro/specs/price-pilot/tasks.md`

## 🐛 Troubleshooting

**Common Issues:**
- **Port conflicts**: Use `lsof -ti:8000 | xargs kill -9` to free ports
- **Docker issues**: Try `docker-compose down && docker-compose up --build`
- **No products**: Run `python backend/run_scrapers.py` to populate data

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## 📈 Performance

- ⚡ **Sub-second search** with fuzzy matching
- 🔄 **Real-time updates** via WebSocket connections
- 📱 **Mobile-optimized** responsive design
- 🚀 **CDN-ready** static assets

## 🔒 Privacy & Ethics

- 🤖 **Respectful scraping** with rate limiting
- 🔐 **No personal data** collection
- 📊 **Transparent pricing** - no affiliate links
- ⚖️ **Fair use** compliance with robots.txt

## 📄 License

MIT License - feel free to use this project for learning, personal use, or commercial applications.

---

**Built with ❤️ for developers who love clean code and great UX**

⭐ **Star this repo** if PricePilot helps you save money on tech purchases!