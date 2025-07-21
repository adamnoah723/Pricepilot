@echo off
echo 🚀 Starting PricePilot Development Environment
echo =============================================

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js is installed

REM Install root dependencies
echo 📦 Installing root dependencies...
npm install

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Install backend dependencies
echo 🐍 Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo 🎉 Setup complete! Starting development servers...
echo.
echo Frontend will be available at: http://localhost:3001
echo Backend will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop both servers
echo.

REM Start both frontend and backend
npm run dev