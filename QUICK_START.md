# 🚀 Quick Start Guide

## One-Command Setup & Run

### For macOS/Linux:
```bash
./start-dev.sh
```

### For Windows:
```cmd
start-dev.bat
```

### Manual Setup (if scripts don't work):
```bash
# 1. Install dependencies
npm install
cd frontend && npm install && cd ..
cd backend && pip install -r requirements.txt && cd ..

# 2. Start development servers
npm run dev
```

## What This Does:

1. ✅ **Installs all dependencies** (root, frontend, backend)
2. ✅ **Starts both servers simultaneously**:
   - Frontend: http://localhost:3001
   - Backend: http://localhost:8000
3. ✅ **Enables hot reload** for development

## Expected Result:

After running the setup, you should see:
- ✅ No more red files/folders in your IDE
- ✅ Frontend loads at http://localhost:3001
- ✅ Backend API responds at http://localhost:8000
- ✅ All TypeScript errors resolved
- ✅ Full price comparison functionality working

## Troubleshooting:

### If you get permission errors on macOS/Linux:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### If Node.js is not installed:
1. Download from https://nodejs.org/ (LTS version)
2. Install and restart your terminal
3. Run the setup script again

### If Python dependencies fail:
```bash
cd backend
python -m pip install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

### If ports are already in use:
- Frontend port 3001: Change in `frontend/vite.config.ts`
- Backend port 8000: Change in `package.json` scripts

## Next Steps After Setup:

1. 🔍 **Test the search functionality**
2. 📊 **View price comparisons**  
3. 🛒 **Browse product categories**
4. 🔧 **Add sample data** with `npm run scrape`

## Development Commands:

```bash
npm run dev          # Start both frontend & backend
npm run dev:frontend # Frontend only
npm run dev:backend  # Backend only
npm run build        # Build for production
npm run scrape       # Run price scrapers
```