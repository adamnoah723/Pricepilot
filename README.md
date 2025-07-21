# PricePilot - Smart Price Comparison Platform

PricePilot is a comprehensive price comparison platform for high-ticket tech items like laptops, headphones, and speakers. It scrapes prices from multiple vendors and provides users with real-time price comparisons.

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **PostgreSQL** (for database)
- **Docker & Docker Compose** (optional, for containerized setup)

### Option 1: Docker Setup (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/your/project
   ```

2. **Create environment files:**
   ```bash
   # Backend environment
   cp backend/.env.example backend/.env
   
   # Frontend environment  
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services with Docker:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - **Frontend:** http://localhost:3001
   - **Backend API:** http://localhost:8001
   - **API Docs:** http://localhost:8001/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # Install PostgreSQL if not already installed
   # On macOS:
   brew install postgresql
   brew services start postgresql
   
   # Create database
   createdb pricepilot
   ```

5. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the backend server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

## 🔧 Port Configuration

The application uses the following ports by default:

- **Frontend:** 3001
- **Backend:** 8001 (mapped from internal 8000)
- **Database:** 5432

### Changing Ports

If you need to use different ports:

1. **Frontend port** - Edit `frontend/vite.config.ts`:
   ```typescript
   server: {
     port: YOUR_PORT,
     host: true,
   }
   ```

2. **Backend port** - Edit `docker-compose.yml` or run uvicorn with different port:
   ```bash
   uvicorn app.main:app --port YOUR_PORT
   ```

3. **Update CORS** - Edit `backend/app/main.py` to allow your frontend port:
   ```python
   allow_origins=["http://localhost:YOUR_FRONTEND_PORT"]
   ```

## 🕷️ Running Scrapers

To populate the database with product data:

1. **Run the scraper pipeline:**
   ```bash
   cd backend
   python run_scrapers.py
   ```

2. **Run specific vendor scraper:**
   ```bash
   python run_scrapers.py --vendor amazon --queries "MacBook Pro" "iPad"
   ```

3. **Schedule regular scraping** (optional):
   ```bash
   # Add to crontab for daily scraping at 2 AM
   0 2 * * * cd /path/to/backend && python run_scrapers.py
   ```

## 📊 API Endpoints

### Core Endpoints

- `GET /api/health` - Health check
- `GET /api/categories` - Get all categories
- `GET /api/vendors` - Get all vendors
- `GET /api/search?q={query}` - Search products
- `GET /api/products` - Get products with filtering
- `GET /api/products/{id}` - Get product details
- `GET /api/products/{id}/similar` - Get similar products
- `GET /api/autocomplete?q={query}` - Search autocomplete
- `GET /api/scraper-status` - Get scraper run status

### API Documentation

Visit http://localhost:8001/docs for interactive API documentation.

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation

### Frontend (React)
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **React Query** - Data fetching
- **React Router** - Navigation

### Scrapers
- **Selenium** - Web scraping (Amazon)
- **aiohttp** - HTTP client (Best Buy, Walmart)
- **BeautifulSoup** - HTML parsing
- **Configurable scrapers** - For brand websites

## 🛠️ Development

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change ports in configuration files
   - Kill existing processes: `lsof -ti:PORT | xargs kill -9`

2. **Database connection errors:**
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists

3. **CORS errors:**
   - Check frontend URL in backend CORS configuration
   - Ensure ports match between frontend and backend

4. **Scraper issues:**
   - Install Chrome/Chromium for Selenium
   - Check rate limiting settings
   - Verify website selectors are current

### Logs

- **Backend logs:** Check console output or configure logging
- **Frontend logs:** Check browser developer console
- **Docker logs:** `docker-compose logs [service_name]`

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review API documentation at `/docs`
- Check application logs for error details