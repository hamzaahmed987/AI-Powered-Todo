# 🚀 INSTALL NOW - Copy & Paste Commands

**All commands to install and run the fullstack app - just copy and paste!**

---

## 📦 BACKEND INSTALLATION

### Step 1: Navigate to Backend
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

### Step 3: Install ALL Backend Dependencies

**Copy this entire command:**
```bash
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 pydantic==2.5.0 pydantic-settings==2.1.0 python-dotenv==1.0.0 pytest==7.4.3 pytest-asyncio==0.21.1 httpx==0.25.2
```

**OR use requirements file (easier):**
```bash
pip install -r requirements-minimal.txt
```

### Step 4: Create Environment File
```bash
cp .env.example .env
```

Windows:
```bash
copy .env.example .env
```

### Step 5: Run Backend
```bash
python -m uvicorn app.simple_main:app --reload
```

**Stop with:** `CTRL+C`

---

## 💻 FRONTEND INSTALLATION

### Step 1: Navigate to Frontend
```bash
cd frontend
```

### Step 2: Install ALL Frontend Dependencies
```bash
npm install
```

**Or individual packages:**
```bash
npm install @reduxjs/toolkit react-redux axios
```

### Step 3: Create Environment File
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
```

Windows:
```bash
echo NEXT_PUBLIC_API_URL=http://localhost:8000/api > .env.local
```

### Step 4: Run Frontend
```bash
npm run dev
```

**Stop with:** `CTRL+C`

---

## 🔄 FULL INSTALLATION (Both at Once)

### Linux/Mac Script (save as `install.sh` and run `bash install.sh`)
```bash
#!/bin/bash

echo "🚀 Installing Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
cp .env.example .env

echo "🚀 Installing Frontend..."
cd ../frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

echo "✅ Installation Complete!"
echo "Run in separate terminals:"
echo "  Backend:  cd backend && source venv/bin/activate && python -m uvicorn app.simple_main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
```

### Windows Script (save as `install.bat` and double-click)
```batch
@echo off
echo 🚀 Installing Backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements-minimal.txt
copy .env.example .env

echo 🚀 Installing Frontend...
cd ..\frontend
npm install
echo NEXT_PUBLIC_API_URL=http://localhost:8000/api > .env.local

echo ✅ Installation Complete!
echo Run in separate terminals:
echo   Backend:  cd backend ^&^& venv\Scripts\activate ^&^& python -m uvicorn app.simple_main:app --reload
echo   Frontend: cd frontend ^&^& npm run dev

pause
```

---

## ✅ VERIFICATION COMMANDS

### Check Installations
```bash
# Check Python
python --version

# Check Node
node --version
npm --version

# Check installed packages
pip list | grep -E "fastapi|sqlalchemy|pydantic"
npm list | grep -E "redux|react"
```

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Get all tasks
curl http://localhost:8000/api/tasks

# API documentation
# Open browser: http://localhost:8000/docs
```

### Test Frontend
```bash
# Open browser: http://localhost:3000
```

---

## 🚀 START RUNNING THE APP

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate              # Windows
python -m uvicorn app.simple_main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Expected output:
```
> next dev
✓ Ready in XXXms on http://localhost:3000
```

### Terminal 3 - Testing (Optional)
```bash
# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Buy groceries"}'

# List all tasks
curl http://localhost:8000/api/tasks
```

---

## 🔗 Access Your App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ❌ TROUBLESHOOTING QUICK FIXES

### Port Already in Use
```bash
# Change port for backend
python -m uvicorn app.simple_main:app --reload --port 8001

# Change port for frontend
npm run dev -- -p 3001
```

### Module Not Found
```bash
# Make sure venv is activated
which python  # should show venv path

# Reinstall packages
pip install -r requirements-minimal.txt
```

### Node_modules Issues
```bash
# Clean and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database Issues
```bash
# Reset database
rm backend/todo.db  # or: del backend\todo.db
# Restart backend - will auto-create
```

---

## 📊 Package Sizes (Reference)

| Item | Size | Time |
|------|------|------|
| Backend venv | ~150MB | 2-3 min |
| Frontend node_modules | ~500MB | 3-5 min |
| **Total** | **~650MB** | **5-8 min** |

---

## ✨ What Gets Installed

### Backend Packages
```
fastapi          0.104.1   - Web framework
uvicorn          0.24.0    - Server
sqlalchemy       2.0.23    - Database ORM
pydantic         2.5.0     - Validation
python-dotenv    1.0.0     - Environment vars
pytest           7.4.3     - Testing
```

### Frontend Packages
```
next             ^14.0     - React framework
react            ^18.0     - UI library
@reduxjs/toolkit ^1.9.0    - State management
react-redux      ^8.1.0    - Redux bindings
axios            ^1.6.0    - HTTP client
```

---

## 🎯 Summary

### Copy These Commands in Order:

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
cp .env.example .env
python -m uvicorn app.simple_main:app --reload
```

**Frontend Setup (in another terminal):**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local
npm run dev
```

**Done!** App running at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 📞 Need Help?

- **Installation issues**: Check INSTALLATION_COMMANDS.md
- **Setup problems**: Check SETUP_GUIDE.md
- **Want quick start**: See QUICK_START.md
- **Code details**: See CODE_REVIEW.md

---

**That's it! You're ready to go! 🚀**

Questions? Refer to the detailed guides, but these commands should work as-is.
