# PricePilot Setup Guide

This guide will help you get PricePilot running on your local machine in just a few minutes.

## 🚀 Quick Start (Recommended)

The easiest way to run PricePilot is using Docker, which handles all dependencies automatically.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the Repository
```bash
git clone https://github.com/adamnoah723/Pricepilot.git
cd Pricepilot
```

### 2. Start with Docker Compose
```bash
# Start all services (database, backend, frontend)
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

### 3. Access the Application
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Populate with Sample Data
```bash
# Run the scrapers to get product data
docker-compose exec backend python run_scrapers.py
```

That's it! 🎉 You should now have a fully functional price comparison website.

---

## 🛠 Manual Setup (Advanced)

If you prefer to run services individually or don't want to use Docker:

### Prerequisites
- Python 3.9+ with pip
- Node.js 18+ with npm
- PostgreSQL (optional, SQLite is used by default)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env if needed (default settings work for local development)
   ```

5. **Start the backend server**
   ```bash
   # Option 1: Using the custom start script
   python start_server.py
   
   # Option 2: Using uvicorn directly
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Populate with data (in a new terminal)**
   ```bash
   cd backend
   python run_scrapers.py
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:3001

---

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```env
# Database Configuration
DATABASE_URL=sqlite:///./pricepilot.db

# Scraper Configuration
SCRAPER_HEADLESS=true
SCRAPER_MAX_RETRIES=3
AMAZON_RATE_LIMIT=1.0
BESTBUY_RATE_LIMIT=0.5
WALMART_RATE_LIMIT=0.5
BRAND_RATE_LIMIT=2.0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

**Frontend (.env)**
```env
# API Configuration
VITE_API_URL=http://localhost:8000
```

### Port Configuration

Default ports:
- Frontend: 3001
- Backend: 8000
- Database: 5432 (PostgreSQL, if used)

To change ports, update:
1. `docker-compose.yml` for Docker setup
2. Backend `.env` file and start command
3. Frontend `.env` file (`VITE_API_URL`)

---

## 📊 Using the Application

### 1. Search for Products
- Use the search bar to find products (e.g., "MacBook Pro", "Sony headphones")
- Browse by categories: Laptops, Headphones, Speakers

### 2. Compare Prices
- Click on any product to see detailed price comparison
- View prices from Amazon, Best Buy, Walmart, and brand websites
- See discount percentages and stock status
- Click "View Deal" to go directly to the vendor's product page

### 3. Data Freshness
- Price data freshness is shown for each vendor
- Scrapers run automatically to keep data current
- Manual scraper runs: `python backend/run_scrapers.py`

---

## 🕷️ Scraper Information

PricePilot includes scrapers for:
- **Amazon**: Real product data using Selenium
- **Best Buy**: Mock data (real scraper can be blocked)
- **Walmart**: Mock data (real scraper can be blocked)
- **Brand Websites**: Mock data (configurable for different brands)

### Running Scrapers Manually

```bash
# Run all scrapers
python backend/run_scrapers.py

# Or with Docker
docker-compose exec backend python run_scrapers.py
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:3001 | xargs kill -9  # Frontend
```

**2. Docker Issues**
```bash
# Restart Docker services
docker-compose down
docker-compose up --build

# View logs
docker-compose logs backend
docker-compose logs frontend
```

**3. Database Issues**
```bash
# Reset database (will lose data)
rm backend/pricepilot.db
python backend/run_scrapers.py
```

**4. Frontend Not Loading**
- Check that backend is running on port 8000
- Verify `VITE_API_URL` in `frontend/.env`
- Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)

**5. No Products Showing**
- Run scrapers to populate database: `python backend/run_scrapers.py`
- Check backend logs for scraper errors
- Verify database has data: `sqlite3 backend/pricepilot.db "SELECT COUNT(*) FROM products;"`

### Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs` or terminal output
2. Verify all services are running: `docker-compose ps`
3. Ensure ports 3001 and 8000 are available
4. Try restarting: `docker-compose restart`

---

## 🏗️ Development

### Project Structure
```
PricePilot/
├── backend/           # FastAPI backend
│   ├── app/          # Core application
│   ├── scrapers/     # Web scrapers
│   └── alembic/      # Database migrations
├── frontend/         # React frontend
│   └── src/          # Source code
├── scrapers/         # Scraper implementations
└── .kiro/           # Project specifications
```

### Making Changes

1. **Backend changes**: Server auto-reloads with `--reload` flag
2. **Frontend changes**: Vite dev server auto-reloads
3. **Database changes**: Use Alembic migrations in `backend/alembic/`

### Adding New Scrapers

1. Create new scraper in `scrapers/` extending `BaseScraper`
2. Add vendor to database in `backend/run_scrapers.py`
3. Configure scraper settings in backend `.env`

---

## 📝 License

This project is open source and available under the MIT License.