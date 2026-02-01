# Quick Start: Todo App with Neon PostgreSQL & OpenAI

Get the AI-Powered Todo App running in **under 15 minutes**.

**Estimated Time**: 12-15 minutes
**Difficulty**: Beginner-friendly

---

## Prerequisites

Before you start, make sure you have:

- ✅ **Python 3.11+** installed
  Check: `python --version`

- ✅ **Node.js 18+** installed
  Check: `node --version`

- ✅ **uv package manager** installed
  Check: `uv --version`
  Install: `pip install uv`

- ✅ **Git** installed (to clone repo)
  Check: `git --version`

---

## 5-Minute Setup: Get Your Credentials

### 1️⃣ Get Neon Database (2 minutes)

1. Go to https://neon.tech → Click **"Sign Up"**
2. Sign up with GitHub/Google/Email
3. Create a new project:
   - Name: `todo-app`
   - Region: Closest to you
4. Copy your connection string from "Connection Details"
5. **Save it** - you'll need it in Step 3

```
postgresql://user:password@host/dbname?sslmode=require
```

### 2️⃣ Get Google Gemini API Key (1 minute)

1. Go to https://aistudio.google.com → Sign in with Google
2. Click **"Get API key"** in sidebar
3. Click **"Create API key in new project"**
4. Copy the key (format: `AIzaSy...`)
5. **Save it** - you'll need it in Step 5

**Why Gemini?**
- ✅ **100% FREE** (1500 requests/day)
- ✅ **No payment required**
- ✅ **Fast responses** (~1-2 seconds)
- ✅ **High quality** task analysis

### 3️⃣ Generate JWT Secret (1 minute)

Run this command to generate a secure secret:

**macOS/Linux:**
```bash
openssl rand -hex 32
```

**Windows or if openssl not installed:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Save the output** - you'll need it in Step 5

---

## 10-Minute Setup: Run the App

### Step 1: Clone/Navigate to Project

```bash
# If you don't have the project yet:
# git clone <repo-url>
# cd todo-app

# If you already have it:
cd path/to/todo-app
```

### Step 2: Setup Backend Environment

```bash
cd backend
cp .env.example .env
```

Now edit `backend/.env` and fill in your values from the credential setup above:

```bash
# Paste your Neon connection string here
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOST/YOUR_DB?sslmode=require

# Paste your OpenAI API key here
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE

# Paste your generated JWT secret here
JWT_SECRET_KEY=YOUR_GENERATED_64_CHARACTER_STRING

# Keep these as-is for local development
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=7

DEBUG=true
HOST=0.0.0.0
PORT=8000

ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

ENVIRONMENT=development
LOG_LEVEL=INFO

AI_TIMEOUT_SECONDS=3
AI_RATE_LIMIT_CALLS=10
AI_RATE_LIMIT_WINDOW=60

SQL_ECHO=false
```

### Step 3: Install Backend Dependencies

```bash
# Still in backend/ directory
uv sync
```

**Expected output:**
```
Resolved X dependencies in XXms
...
Installation complete
```

### Step 4: Run Database Migrations

```bash
# Still in backend/ directory
uv run alembic upgrade head
```

**Expected output:**
```
INFO [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, done
```

### Step 5: Setup Backend Environment & Start Server

```bash
# Still in backend/ directory
cp .env.example .env
```

Edit `backend/.env` and set:
- `DATABASE_URL` = your Neon connection string
- `GEMINI_API_KEY` = your Gemini API key from Step 2
- `JWT_SECRET_KEY` = run `openssl rand -hex 32` and paste result

Then run:
```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Keep this terminal running. Your backend is now live!

✅ **Backend ready!** Go to http://localhost:8000/docs to see API documentation.

### Step 6: Setup Frontend Environment

Open a **NEW TERMINAL WINDOW** and run:

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api

NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=AI Todo App
```

### Step 7: Start Frontend Server

```bash
# Still in frontend/ directory
npm run dev
```

**Expected output:**
```
> next dev
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  ▲ Ready in 2.5s
```

---

## 🎉 Done!

Your app is now running!

| Component | URL | Status |
|-----------|-----|--------|
| **Frontend** | http://localhost:3000 | ✅ Live |
| **Backend API** | http://localhost:8000 | ✅ Live |
| **API Docs** | http://localhost:8000/docs | ✅ Available |
| **Database** | Neon (serverless) | ✅ Connected |
| **AI** | Google Gemini 2.0 Flash | ✅ Ready (FREE!) |

---

## Next Steps

### 1. Create an Account

1. Go to http://localhost:3000
2. Click **"Create Account"** (or "Sign up")
3. Fill in form:
   - **Name**: Your name
   - **Email**: Any email
   - **Password**: 12+ chars with uppercase, lowercase, number (e.g., `MyPassword123`)
   - **Confirm Password**: Same as above
4. Click **"Create Account"**

### 2. Log In

1. Click **"Sign in"**
2. Enter your email and password
3. Click **"Sign In"**

### 3. Create Your First Task

1. Click **"+ New Task"**
2. Fill in:
   - **Title**: "Buy groceries"
   - **Priority**: Medium/High
   - **Description**: "Milk, eggs, bread"
   - **Deadline**: (optional) Pick tomorrow's date
3. Click **"Create"**

### 4. See AI in Action

After creating the task, you'll see:
- **AI-Powered Priority**: OpenAI automatically analyzes and suggests a priority level
- **Status**: Shows as "Pending"
- **Options**: Edit, delete, or mark as complete

---

## Troubleshooting

### "Cannot connect to database"

```
Error: Database connection failed
```

**Fix:**
1. Verify DATABASE_URL in `backend/.env` is correct
2. Copy directly from Neon Console (don't retype)
3. Check it includes `?sslmode=require` at the end
4. Verify Neon project is not paused:
   - Go to https://console.neon.tech
   - Click your project → Click "Resume" if needed

### "Invalid API key"

```
Error: Incorrect API key provided
```

**Fix:**
1. Verify your OpenAI API key:
   - Must start with `sk-proj-`
   - Check for extra spaces (common issue)
   - Regenerate if needed: https://platform.openai.com/api-keys
2. Ensure payment method is added to OpenAI account
3. Wait 5-10 minutes for account activation

### "Port 8000 already in use"

```
Error: [Errno 48] Address already in use
```

**Fix:**
1. Kill the process:
   ```bash
   # macOS/Linux
   lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill

   # Windows
   netstat -ano | findstr :8000
   taskkill /PID [PID] /F
   ```
2. Or use a different port:
   ```bash
   PORT=8001 uv run uvicorn app.main:app --reload
   ```

### "Module not found: openai"

```
ModuleNotFoundError: No module named 'openai'
```

**Fix:**
1. Install dependencies:
   ```bash
   cd backend
   uv sync
   ```
2. Verify you're in `backend/` directory

### "Cannot connect to http://localhost:3000"

**Fix:**
1. Verify frontend is running (`npm run dev` running in terminal)
2. Wait 30 seconds for Next.js to compile
3. Check you're using correct URL: `http://localhost:3000` (not `localhost:3000` or `https`)

### "Registration fails"

**Common issues:**
- Password must be 12+ characters
- Password must include uppercase, lowercase, and number
- Email already registered (try different email)

---

## How It Works

### Architecture Overview

```
Frontend (Next.js)
    ↓ (API calls)
Backend API (FastAPI)
    ↓ (SQL queries)
Database (Neon PostgreSQL)
    ↓ (task analysis)
AI (Google Gemini 2.0 Flash via Agents SDK)
```

### Task Creation Flow

1. **User creates task** in frontend
2. **Frontend validates** form with Formik+Yup
3. **Frontend sends** to backend API
4. **Backend validates** with Pydantic schemas
5. **Backend creates** task in Neon database
6. **Gemini analyzes** task description via OpenAI Agents SDK
7. **Backend stores** AI priority & estimates
8. **Frontend shows** completed task with AI data

### Data Models

**User:**
- ID (UUID)
- Email (unique)
- Name (optional)
- Password (hashed with bcrypt)

**Task:**
- ID (UUID)
- Title (required)
- Description (optional)
- Status (pending, in_progress, completed)
- Priority (low, medium, high)
- Deadline (optional, ISO date)
- AI Priority (suggested by OpenAI)
- Created/Updated timestamps

---

## Useful Commands

### Backend Commands

```bash
cd backend

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload

# Test database connection
uv run python -c "from app.database.session import check_db_connection; print(check_db_connection())"

# Interactive Python shell
uv run python

# Run tests
uv run pytest

# Format code
uv run black app/

# Check linting
uv run ruff check app/
```

### Frontend Commands

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run production build locally
npm run start

# Check linting
npm run lint

# Format code
npm run format
```

---

## Useful Links

**Development:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- API ReDoc: http://localhost:8000/redoc

**External Services:**
- Neon Console: https://console.neon.tech
- OpenAI Platform: https://platform.openai.com
- OpenAI API Keys: https://platform.openai.com/api-keys
- OpenAI Billing: https://platform.openai.com/account/billing

**Documentation:**
- Full Setup Guide: `backend/ENV_SETUP_GUIDE.md`
- Architecture Docs: `FULLSTACK_ARCHITECTURE.md`
- API Documentation: Visit http://localhost:8000/docs (when running)

---

## Next: Production Deployment

When ready to deploy:

1. **Choose a hosting service:**
   - Backend: Fly.io, Railway, Render, Heroku
   - Frontend: Vercel (recommended), Netlify, Railway
   - Database: Keep Neon (serverless)

2. **Environment variables:**
   - Set all `.env` variables in hosting platform
   - Use strong, unique secrets for production
   - Never commit `.env` files

3. **SSL/HTTPS:**
   - Most hosting platforms provide free SSL
   - Required for production

4. **Monitoring:**
   - Set up error tracking (Sentry optional)
   - Monitor database usage (Neon dashboard)
   - Monitor API usage (OpenAI dashboard)

For detailed production setup, see `FULLSTACK_ARCHITECTURE.md`.

---

## Getting Help

**If something doesn't work:**

1. **Check Troubleshooting section** (above)
2. **Read full guide**: `backend/ENV_SETUP_GUIDE.md`
3. **Check error messages** carefully
4. **Verify all steps** were completed correctly
5. **Create GitHub issue** with error details

---

**Happy Building! 🚀**

Questions? Check the docs or create an issue in the repository.

---

**Last Updated**: December 2024
**Tested With**: Python 3.11+, Node.js 18+, Next.js 14, FastAPI 0.104.1
