# 🚀 START HERE

**AI-Powered Todo App - Getting Started Guide**

Welcome! This guide will get you up and running in 15 minutes.

---

## ⏱️ What You Need (Preparation: 5 minutes)

Before you start, you'll need three simple things:

### 1️⃣ Neon Database (Free)

```
1. Go to https://neon.tech
2. Click "Sign Up" (use GitHub for fastest signup)
3. Create a project called "todo-app"
4. Copy your connection string (looks like: postgresql://user:pass@host/db?sslmode=require)
5. Save it somewhere - you'll need it in 5 minutes
```

**Why Neon?** Free serverless PostgreSQL database. No credit card required.

### 2️⃣ Google Gemini API Key (Free)

```
1. Go to https://aistudio.google.com
2. Sign in with any Google account
3. Click "Get API key" in sidebar
4. Click "Create API key in new project"
5. Copy your API key (looks like: AIzaSy...)
6. Save it - you'll need it in 5 minutes
```

**Why Gemini?** Free AI model (1500 requests/day). No payment needed.

### 3️⃣ Generate a Secret Key (2 minutes)

Open terminal and run ONE of these:

**Option A: macOS/Linux**
```bash
openssl rand -hex 32
```

**Option B: Windows (PowerShell)**
```powershell
[BitConverter]::ToString([byte[]]$((1..32) | ForEach-Object { Get-Random -Max 256 })) -replace '-', ''
```

**Option C: Python (Any OS)**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (a 64-character string) - you'll need it in 5 minutes.

---

## 🎯 Installation (Execution: 10 minutes)

### Step 1: Clone and Navigate (1 minute)

```bash
# Navigate to project directory
cd "E:\Panaversity Hackathon\Todo App"

# Or clone if you don't have it
git clone <repo-url> todo-app
cd todo-app
```

### Step 2: Setup Backend (3 minutes)

```bash
cd backend

# Copy example env file
cp .env.example .env
# (On Windows: copy .env.example .env)

# Edit .env and fill in your values:
# DATABASE_URL=<paste your Neon connection string>
# GEMINI_API_KEY=<paste your Gemini API key>
# JWT_SECRET_KEY=<paste the secret you generated>
# Then save the file

# Install dependencies
uv sync

# Run database migrations
uv run alembic upgrade head

# Start the backend
uv run uvicorn app.main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 3: Setup Frontend (2 minutes)

Open **new terminal window** and run:

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
  ▲ Next.js 16.0.7
  - Local:        http://localhost:3000
  ▲ Ready in 2.5s
```

### Step 4: Test in Browser (4 minutes)

Open http://localhost:3000 in your browser

```
1. Click "Create Account"
2. Fill in the form:
   - Name: Your Name
   - Email: test@example.com
   - Password: SecurePass123 (needs 12+ chars, uppercase, lowercase, number)
3. Click "Create Account"
4. You should see the dashboard
5. Click "Create Task"
6. Enter a task title like "Review quarterly reports"
7. You should see AI suggestions appear!
```

---

## ✅ Success! You're Done!

If you can:
- ✅ Create an account
- ✅ See the dashboard
- ✅ Create a task
- ✅ See AI priority suggestions

**Congratulations! Everything is working!** 🎉

---

## 📚 What's Next?

### Option A: Explore More
- See all tasks at: http://localhost:3000
- Edit a task by clicking on it
- Delete a task with the delete button
- Try creating tasks with different titles to see different AI suggestions

### Option B: Run Full Verification
See the complete test suite: `INTEGRATION_VERIFICATION.md`
- Test all API endpoints
- Test error scenarios
- Test security features
- Takes about 30-60 minutes

### Option C: Understand How It Works
Read the documentation:
- `QUICK_START_NEON.md` - Quick reference guide
- `FRONTEND_BACKEND_SETUP.md` - How frontend and backend connect
- `DOCUMENTATION_INDEX.md` - Complete documentation map

### Option D: Deploy to Production
See: `QUICK_START_NEON.md` section "For Production"

---

## 🆘 Something Went Wrong?

### Backend won't start
```bash
# Check if port 8000 is in use
# Or check the error message and see:
# backend/ENV_SETUP_GUIDE.md section "Troubleshooting"
```

### Frontend won't load at localhost:3000
```bash
# Check if npm install completed successfully
# Make sure you're in frontend directory
# Try: npm run dev again
```

### "Cannot reach backend" error
```bash
# Make sure backend is running on terminal 1
# Check that NEXT_PUBLIC_API_URL is set correctly:
# Should be: http://localhost:8000/api/v1
```

### AI suggestions are showing null
```bash
# Make sure GEMINI_API_KEY is set in backend/.env
# Check the GEMINI_API_KEY is correct (should start with AIzaSy)
# Restart backend: Ctrl+C and run uvicorn again
```

### Can't login after registration
```bash
# Check password meets requirements:
# - At least 12 characters
# - Has uppercase letter
# - Has lowercase letter
# - Has number
# Example: SecurePass123
```

### More help needed?
See complete troubleshooting:
- `backend/ENV_SETUP_GUIDE.md` - Section 6
- `FRONTEND_BACKEND_SETUP.md` - Troubleshooting section
- `INTEGRATION_VERIFICATION.md` - Troubleshooting reference

---

## 🔑 Keep These Handy

When you need to:

| Need | Go To |
|------|-------|
| Setup help | `backend/ENV_SETUP_GUIDE.md` |
| API documentation | http://localhost:8000/docs |
| Test everything | `INTEGRATION_VERIFICATION.md` |
| Understand architecture | `FRONTEND_BACKEND_SETUP.md` |
| Find any document | `DOCUMENTATION_INDEX.md` |
| Deploy to production | `QUICK_START_NEON.md` |

---

## 🎓 Technology Stack (For Reference)

**Backend**
- FastAPI (Python web framework)
- PostgreSQL via Neon (database)
- SQLAlchemy (ORM)
- Google Gemini 2.0 Flash (AI)

**Frontend**
- Next.js 16 (React framework)
- Redux Toolkit (state management)
- TypeScript (type safety)

**Authentication**
- JWT tokens (stateless auth)
- Bearer token in Authorization header

---

## 📊 What Just Happened?

You now have:

✅ **Backend API** running on http://localhost:8000
   - Handles user registration/login
   - Manages tasks (create, read, update, delete)
   - Provides AI-powered suggestions
   - Stores everything in Neon database

✅ **Frontend App** running on http://localhost:3000
   - User interface for the Todo app
   - Communicates with backend API
   - Stores auth token in browser
   - Shows AI suggestions

✅ **AI Features**
   - Google Gemini analyzes task descriptions
   - Provides priority suggestions ("low", "medium", "high", "urgent")
   - Estimates time needed for each task

✅ **Database**
   - Neon serverless PostgreSQL
   - Stores users and tasks
   - No local database needed

---

## 🎯 Quick Commands Reference

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Optional - Run tests
cd backend
uv run pytest

# Verify database connection
curl http://localhost:8000/health

# View API documentation
http://localhost:8000/docs

# View interactive ReDoc
http://localhost:8000/redoc
```

---

## 🚀 You're Ready!

Everything is set up and ready to go.

**Next:** Open http://localhost:3000 and create your first task! 🎉

---

## 📞 Need Help?

1. **Quick help**: Read the "Troubleshooting" section above
2. **Detailed help**: See the document specific to your issue:
   - Backend → `backend/ENV_SETUP_GUIDE.md`
   - Frontend → `FRONTEND_BACKEND_SETUP.md`
   - Testing → `INTEGRATION_VERIFICATION.md`
3. **Understanding everything**: Read `DOCUMENTATION_INDEX.md`

---

**Version**: December 9, 2025
**Status**: ✅ Ready to Go
**Time to Running**: 15 minutes

Enjoy your AI-powered Todo App! 🚀
