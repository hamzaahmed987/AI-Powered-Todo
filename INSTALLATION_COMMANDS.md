# Installation Commands - Complete Guide

This document provides all the commands needed to install dependencies for the fullstack Todo app.

---

## 🔧 Backend Setup (FastAPI + SQLAlchemy)

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

#### Option A: Install from Minimal Requirements (RECOMMENDED)
```bash
pip install -r requirements-minimal.txt
```

#### Option B: Install from Full Requirements
```bash
pip install -r requirements.txt
```

#### Option C: Install Packages Individually

**Core Packages (Required):**
```bash
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install sqlalchemy==2.0.23
pip install pydantic==2.5.0
pip install pydantic-settings==2.1.0
```

**Utilities (Recommended):**
```bash
pip install python-dotenv==1.0.0
```

**Testing (Optional):**
```bash
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install httpx==0.25.2
```

### Step 4: Verify Installation
```bash
# Check Python packages
pip list

# Test imports
python -c "from fastapi import FastAPI; print('✓ FastAPI')"
python -c "from sqlalchemy import __version__; print(f'✓ SQLAlchemy {__version__}')"
python -c "from pydantic import BaseModel; print('✓ Pydantic')"
python -c "from uvicorn import __version__; print(f'✓ Uvicorn {__version__}')"
```

### Step 5: Set Up Environment Variables
```bash
# Copy example file
cp .env.example .env

# On Windows:
copy .env.example .env
```

### Step 6: Run Backend
```bash
python -m uvicorn app.simple_main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 [press SHIFT+C to quit]
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete
```

---

## 💻 Frontend Setup (Next.js + Redux)

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Check Node.js and npm

**Check Node Version (should be 18+):**
```bash
node --version
# Output: v18.x.x or higher
```

**Check npm Version:**
```bash
npm --version
# Output: 9.x.x or higher
```

**If Node is not installed, download from:** https://nodejs.org/ (LTS version recommended)

### Step 3: Install Frontend Dependencies

**Option A: Using npm (Recommended)**
```bash
npm install
```

**Option B: Using yarn**
```bash
yarn install
```

**Option C: Install Specific Packages**
```bash
npm install @reduxjs/toolkit@^1.9.0
npm install react-redux@^8.1.0
npm install axios@^1.6.0
npm install next@latest
npm install react@latest
npm install react-dom@latest
```

### Step 4: Verify Installation
```bash
# Check Node packages
npm list

# Test imports by checking if you can run the build
npm run build

# Clean after test
rm -rf .next  # or: rmdir /s .next (Windows)
```

### Step 5: Set Up Environment Variables
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# On Windows:
echo NEXT_PUBLIC_API_URL=http://localhost:8000/api > .env.local
```

### Step 6: Run Frontend
```bash
npm run dev
```

**Expected Output:**
```
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in XXXms
```

---

## 🔄 Complete Installation (Both Backend & Frontend)

### All-in-One Script (Bash/Mac/Linux)
```bash
#!/bin/bash

echo "🚀 Setting up Full Stack Todo App"

# Backend setup
echo "📦 Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
cp .env.example .env

# Frontend setup
echo "📦 Setting up Frontend..."
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

echo "✅ Setup Complete!"
echo ""
echo "To run the app:"
echo "  Terminal 1 (Backend):  cd backend && source venv/bin/activate && python -m uvicorn app.simple_main:app --reload"
echo "  Terminal 2 (Frontend): cd frontend && npm run dev"
```

### All-in-One Script (PowerShell/Windows)
```powershell
# Save as setup.ps1 and run: .\setup.ps1

Write-Host "🚀 Setting up Full Stack Todo App" -ForegroundColor Green

# Backend setup
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-minimal.txt
Copy-Item .env.example .env

# Frontend setup
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
cd ../frontend
npm install
Add-Content -Path .env.local -Value "NEXT_PUBLIC_API_URL=http://localhost:8000/api"

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app:"
Write-Host "  Terminal 1 (Backend):  cd backend && .\venv\Scripts\Activate.ps1 && python -m uvicorn app.simple_main:app --reload"
Write-Host "  Terminal 2 (Frontend): cd frontend && npm run dev"
```

---

## 🐛 Troubleshooting Installation

### Python Issues

**"python: command not found"**
```bash
# Use python3 instead
python3 --version
python3 -m venv venv
```

**"pip: command not found"**
```bash
# Use python -m pip instead
python -m pip --version
python -m pip install fastapi
```

**"Virtual environment not activating"**
```bash
# Windows - use correct command
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

**"ModuleNotFoundError after pip install"**
```bash
# Make sure venv is activated
which python  # Should show path with venv

# Reinstall package
pip install --upgrade --force-reinstall fastapi
```

---

### Node.js Issues

**"node: command not found"**
- Download Node.js from https://nodejs.org/
- Install LTS version
- Restart terminal/IDE

**"npm install fails with permission denied"**
```bash
# Clear npm cache
npm cache clean --force

# Try install again
npm install
```

**"node_modules is corrupted"**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# On Windows:
rmdir /s node_modules
del package-lock.json
npm install
```

**"Port 3000 already in use"**
```bash
# Run on different port
npm run dev -- -p 3001

# Or kill process using port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :3000
kill -9 <PID>
```

---

### Database Issues

**"Database connection error"**
```bash
# Delete old database file
cd backend
rm todo.db  # or: del todo.db (Windows)

# Restart backend - will recreate automatically
python -m uvicorn app.simple_main:app --reload
```

**"Tables don't exist"**
```bash
# Initialize database manually
cd backend
python -c "from app.database.simple_session import init_db; init_db(); print('✓ Database initialized')"
```

---

## ✅ Installation Verification Checklist

### Backend Checklist
- [ ] Virtual environment created and activated
- [ ] All packages installed without errors
- [ ] `python -c "from fastapi import FastAPI"` works
- [ ] `python -c "from sqlalchemy import __version__"` works
- [ ] Backend starts without errors
- [ ] Health check works: `curl http://localhost:8000/health`
- [ ] API docs load: http://localhost:8000/docs

### Frontend Checklist
- [ ] Node.js version is 18+
- [ ] npm version is 9+
- [ ] `npm install` completed without errors
- [ ] `npm list @reduxjs/toolkit` shows installed
- [ ] `.env.local` file created with API URL
- [ ] Frontend starts without errors
- [ ] Page loads: http://localhost:3000

---

## 📋 Package Version Summary

### Backend Packages

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104.1 | Web framework |
| uvicorn | 0.24.0 | ASGI server |
| sqlalchemy | 2.0.23 | ORM & database |
| pydantic | 2.5.0 | Validation |
| pydantic-settings | 2.1.0 | Settings management |
| python-dotenv | 1.0.0 | Environment variables |

### Frontend Packages

| Package | Latest | Purpose |
|---------|--------|---------|
| next | 14+ | React framework |
| react | 18+ | UI library |
| react-dom | 18+ | React DOM |
| @reduxjs/toolkit | 1.9+ | State management |
| react-redux | 8.1+ | Redux for React |
| axios | 1.6+ | HTTP client |

---

## 🚀 Quick Start Commands

### Backend Quick Start
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate
pip install -r requirements-minimal.txt
python -m uvicorn app.simple_main:app --reload
```

### Frontend Quick Start
```bash
cd frontend
npm install
npm run dev
```

### Both Together (3 Terminals)

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.simple_main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Testing (Optional):**
```bash
# Test API
curl http://localhost:8000/health
curl http://localhost:8000/api/tasks
```

---

## 📖 Documentation References

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/en/20/
- **Pydantic**: https://docs.pydantic.dev/
- **Redux Toolkit**: https://redux-toolkit.js.org/
- **Next.js**: https://nextjs.org/docs
- **React**: https://react.dev/

---

## 💡 Tips

1. **Always activate venv before installing packages:**
   ```bash
   source venv/bin/activate  # Mac/Linux
   .\venv\Scripts\activate   # Windows
   ```

2. **Check versions to debug issues:**
   ```bash
   python --version
   node --version
   npm --version
   pip list
   ```

3. **Use `pip freeze` to save current environment:**
   ```bash
   pip freeze > installed-packages.txt
   ```

4. **Clear cache if having strange issues:**
   ```bash
   pip cache purge
   npm cache clean --force
   ```

---

**Last Updated:** December 9, 2025

For more help, see:
- QUICK_START.md - Fast 30-second setup
- SETUP_GUIDE.md - Detailed step-by-step guide
- CODE_REVIEW.md - Code quality & documentation compliance
