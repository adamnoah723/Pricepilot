#!/usr/bin/env node

// Simple setup checker script
const fs = require('fs');
const path = require('path');

console.log('🔍 PricePilot Setup Checker\n');

// Check Node.js version
console.log('📦 Node.js version:', process.version);

// Check if key files exist
const checkFile = (filePath, description) => {
  if (fs.existsSync(filePath)) {
    console.log('✅', description);
    return true;
  } else {
    console.log('❌', description);
    return false;
  }
};

console.log('\n📁 Checking project structure:');
checkFile('frontend/package.json', 'Frontend package.json');
checkFile('frontend/src/App.tsx', 'Main App component');
checkFile('frontend/src/main.tsx', 'App entry point');
checkFile('frontend/tsconfig.json', 'TypeScript config');
checkFile('frontend/vite.config.ts', 'Vite config');
checkFile('frontend/tailwind.config.js', 'Tailwind config');
checkFile('backend/requirements.txt', 'Backend requirements');

console.log('\n📦 Checking dependencies:');
const frontendNodeModules = fs.existsSync('frontend/node_modules');
const rootNodeModules = fs.existsSync('node_modules');

if (frontendNodeModules) {
  console.log('✅ Frontend dependencies installed');
} else {
  console.log('❌ Frontend dependencies missing - run: cd frontend && npm install');
}

if (rootNodeModules) {
  console.log('✅ Root dependencies installed');
} else {
  console.log('❌ Root dependencies missing - run: npm install');
}

console.log('\n🚀 Next steps:');
if (!frontendNodeModules) {
  console.log('1. cd frontend && npm install');
}
if (!rootNodeModules) {
  console.log('2. npm install (in root directory)');
}
console.log('3. npm run dev (to start both frontend and backend)');

console.log('\n📖 For detailed setup instructions, see DEVELOPMENT_SETUP.md');