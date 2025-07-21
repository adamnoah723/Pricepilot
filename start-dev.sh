#!/bin/bash

echo "🚀 Starting PricePilot Development Environment"
echo "============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install backend dependencies (Python)
echo "🐍 Installing backend dependencies..."
cd backend
if command -v pip &> /dev/null; then
    pip install -r requirements.txt
elif command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    echo "⚠️  pip not found. Please install Python dependencies manually:"
    echo "   cd backend && pip install -r requirements.txt"
fi
cd ..

echo ""
echo "🎉 Setup complete! Starting development servers..."
echo ""
echo "Frontend will be available at: http://localhost:3001"
echo "Backend will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start both frontend and backend
npm run dev