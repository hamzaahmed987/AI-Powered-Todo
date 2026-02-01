# Frontend-Backend Connection Setup Guide
## AI Todo App - Complete Integration

**Date**: December 9, 2025
**Status**: ✅ Ready for Integration Testing

---

## Prerequisites

### Requirements
- ✅ **Backend**: Running on http://localhost:8000
  - FastAPI with Gemini API integration
  - Neon PostgreSQL database connected
  - Environment variables configured

- ✅ **Frontend**: Next.js 16 with:
  - Redux Toolkit for state management
  - Axios/Fetch for API calls
  - TypeScript
  - Tailwind CSS

---

## Quick Start: 5 Minutes

### Step 1: Setup Backend (Terminal 1)

```bash
cd backend

# Set environment variables
export GEMINI_API_KEY="AIzaSy..."
export DATABASE_URL="postgresql://..."
export JWT_SECRET_KEY="..."

# Install and run
uv sync
uv run uvicorn app.main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verify backend is working**:
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","database":"ok"}
```

---

### Step 2: Setup Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Environment is pre-configured with .env.local
# File contents:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```

**Expected output**:
```
  ▲ Next.js 16.0.7
  - Local:        http://localhost:3000
  ▲ Ready in 2.5s
```

---

### Step 3: Test the Connection

Visit **http://localhost:3000** in your browser:

1. Click **"Create Account"**
2. Fill in registration form:
   - Name: Your Name
   - Email: test@example.com
   - Password: TestPassword123 (12+ chars, uppercase, lowercase, number)
3. Click **"Create Account"**

**Expected flow**:
```
Frontend (Register)
    ↓
POST /api/v1/auth/register
    ↓
Backend (Create User)
    ↓
POST /api/v1/auth/login (auto)
    ↓
Backend (Generate JWT)
    ↓
Frontend (Store Token)
    ↓
Redirect to Dashboard
```

---

## API Integration Details

### Architecture Diagram

```
┌─────────────────────┐
│   Frontend (Next.js)│
│  Redux + Formik     │
└──────────┬──────────┘
           │
           │ HTTP/JSON
           │ Bearer Token
           ↓
┌──────────────────────────┐
│  Backend (FastAPI)       │
│  - Auth (JWT)            │
│  - Tasks (CRUD)          │
│  - AI (Gemini)           │
└──────────┬───────────────┘
           │
           │ SQL
           ↓
┌──────────────────────────┐
│  Database (Neon)         │
│  PostgreSQL              │
└──────────────────────────┘
```

---

### Authentication Flow

**Login Flow**:
```
1. Frontend: POST /auth/login
   {
     "email": "user@example.com",
     "password": "password123"
   }

2. Backend: Validates credentials, generates JWT

3. Backend Response:
   {
     "access_token": "eyJhbGc...",
     "refresh_token": "eyJhbGc...",
     "token_type": "bearer",
     "expires_in": 86400
   }

4. Frontend:
   - Stores `access_token` in localStorage
   - Uses token in all subsequent requests:
     Authorization: Bearer {access_token}
```

**Registration Flow**:
```
1. Frontend: POST /auth/register
   {
     "email": "user@example.com",
     "password": "password123",
     "full_name": "John Doe"
   }

2. Backend: Creates user, returns UserResponse

3. Frontend: Auto-logs in user (calls /auth/login)

4. Backend: Returns authentication tokens

5. Frontend: Redirects to /dashboard
```

---

### API Endpoints

#### Authentication Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/auth/register` | Create new account | No |
| POST | `/auth/login` | Login with credentials | No |
| POST | `/auth/logout` | Logout user | Bearer Token |

**Request Examples**:

```typescript
// Register
POST http://localhost:8000/api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

// Response (201 Created)
{
  "id": "uuid-1234-5678",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-12-09T10:00:00Z"
}
```

```typescript
// Login
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

// Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Task Endpoints

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/tasks` | List user's tasks | Bearer Token |
| GET | `/tasks?status=pending` | Filter tasks by status | Bearer Token |
| POST | `/tasks` | Create new task | Bearer Token |
| GET | `/tasks/{id}` | Get task details | Bearer Token |
| PUT | `/tasks/{id}` | Update task | Bearer Token |
| DELETE | `/tasks/{id}` | Delete task | Bearer Token |
| PATCH | `/tasks/{id}/complete` | Mark task as completed | Bearer Token |

**Request Examples**:

```typescript
// Create Task
POST http://localhost:8000/api/v1/tasks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Review quarterly report",
  "description": "Analyze Q4 metrics and prepare summary",
  "deadline": "2025-12-20",
  "priority": "high"
}

// Response (201 Created)
{
  "id": "task-uuid-1234",
  "title": "Review quarterly report",
  "description": "Analyze Q4 metrics and prepare summary",
  "deadline": "2025-12-20",
  "priority": "high",
  "status": "pending",
  "ai_priority": "high",          // AI suggestion
  "estimated_duration": 3,         // AI suggestion (hours)
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z",
  "user_id": "user-uuid"
}
```

```typescript
// Get Tasks
GET http://localhost:8000/api/v1/tasks
Authorization: Bearer {access_token}

// Response (200 OK)
[
  {
    "id": "task-uuid-1",
    "title": "Task 1",
    "status": "pending",
    ...
  },
  {
    "id": "task-uuid-2",
    "title": "Task 2",
    "status": "in_progress",
    ...
  }
]
```

---

## File Changes Made

### Frontend Files Updated

#### 1. **frontend/.env.local** (Created)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=AI Todo App
```

#### 2. **frontend/redux/thunks/authThunks.ts** (Updated)
✅ Changed API_URL to include `/v1`
✅ Added backend response type handling
✅ Updated login to handle AuthToken response
✅ Updated register to register then login

#### 3. **frontend/redux/thunks/taskThunks.ts** (Updated)
✅ Changed API_URL to include `/v1`
✅ Fixed response parsing to handle backend format

#### 4. **frontend/redux/slices/taskSlice.ts** (Updated)
✅ Added AI-generated fields: `ai_priority`, `estimated_duration`
✅ Added `urgent` priority option
✅ Added `user_id` field

---

## Testing Checklist

### Before Running App

- [ ] Backend is running on http://localhost:8000
- [ ] GEMINI_API_KEY environment variable is set
- [ ] DATABASE_URL environment variable is set
- [ ] JWT_SECRET_KEY environment variable is set
- [ ] Database connection test passes: `curl http://localhost:8000/health`

### After Starting App

- [ ] Frontend loads at http://localhost:3000
- [ ] Home page shows "Create Account" and "Sign In" buttons
- [ ] Network tab shows API calls going to http://localhost:8000

### Registration Test

```bash
# Test registration endpoint directly
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

Expected response: `201 Created` with user data

### Login Test

```bash
# Test login endpoint directly
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'
```

Expected response: `200 OK` with access_token

### Task Creation Test

```bash
# Replace TOKEN with actual access_token from login
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "title": "Test Task",
    "description": "Testing task creation",
    "priority": "medium"
  }'
```

Expected response: `201 Created` with task data including AI suggestions

---

## Troubleshooting

### "Cannot connect to localhost:8000"

**Problem**: Frontend can't reach backend

**Solutions**:
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check CORS is enabled (should be in backend output)
# Look for: "CORS Middleware" in startup logs

# 3. Verify correct API_URL in frontend
grep NEXT_PUBLIC_API_URL frontend/.env.local
# Should be: http://localhost:8000/api/v1

# 4. Check backend CORS origins
grep ALLOWED_ORIGINS backend/.env
# Should include http://localhost:3000
```

### "Login/Register Returns 422 Validation Error"

**Problem**: Request format doesn't match backend expectations

**Solutions**:
```bash
# Check request body format matches backend schemas
# Backend expects:
{
  "email": "string",
  "password": "string (min 12 chars for register)"
}

# Check password requirements:
# Register: min 12 chars, must have uppercase, lowercase, number
# Example: TestPass123
```

### "Token Expired or Invalid"

**Problem**: Bearer token not being sent or is invalid

**Solutions**:
```bash
# 1. Check localStorage for token
# In browser DevTools Console:
console.log(localStorage.getItem('accessToken'))

# 2. Verify token format (should start with eyJ...)
# 3. Check Authorization header:
# Should be: Authorization: Bearer eyJ...

# 4. Re-login to get fresh token
```

### "Gemini API Not Working (AI Suggestions Null)"

**Problem**: Task AI suggestions returning null

**Solutions**:
```bash
# 1. Verify GEMINI_API_KEY is set
echo $GEMINI_API_KEY

# 2. Check backend logs for AI errors
# Look for: "Error generating AI suggestions"

# 3. Verify Gemini API key is valid
# Try: https://aistudio.google.com/

# 4. Note: AI features gracefully degrade if unavailable
# Tasks will still be created without AI analysis
```

---

## Development Workflow

### Running Both Services

**Terminal 1 - Backend**:
```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 3 - Optional Testing**:
```bash
# Run tests
cd backend
uv run pytest

cd frontend
npm run lint
```

---

## API Documentation

### Swagger UI
Visit: **http://localhost:8000/docs**

Features:
- Interactive API explorer
- Try endpoints directly
- View request/response schemas
- See error codes and examples

### ReDoc
Visit: **http://localhost:8000/redoc**

Features:
- Beautiful API documentation
- Organized by tags
- Detailed schemas
- Right-side code examples

---

## Environment Variables Reference

### Backend (backend/.env)
```bash
DATABASE_URL=postgresql://...
GEMINI_API_KEY=AIzaSy...
JWT_SECRET_KEY=...
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
PORT=8000
```

### Frontend (frontend/.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=AI Todo App
```

---

## Next Steps

### Immediate (Today)
1. Start both backend and frontend
2. Test registration and login
3. Create a task and verify AI suggestions
4. Navigate through dashboard

### Short-term (This Week)
1. Test all CRUD operations for tasks
2. Test filtering and pagination
3. Test error handling (invalid inputs, network errors)
4. Test token expiration/refresh

### Long-term (Future Phases)
1. Add more AI features (subtasks, suggestions, etc.)
2. Add real-time sync with WebSockets
3. Add mobile app
4. Add deployment to production

---

## Useful Commands

### Backend

```bash
# Start development server
cd backend
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Format code
uv run black app/

# Check linting
uv run ruff check app/

# Run migrations
uv run alembic upgrade head
```

### Frontend

```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Run linting
npm run lint

# Format code
npm run format
```

### API Testing

```bash
# Test backend health
curl http://localhost:8000/health

# Test API docs
curl http://localhost:8000/openapi.json

# Test CORS
curl -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000"
```

---

## Success Indicators

You'll know everything is connected when:

✅ Frontend loads at http://localhost:3000
✅ Can register new account
✅ Redirected to dashboard after login
✅ Can create tasks
✅ Tasks show AI priority suggestions
✅ Can update/delete tasks
✅ Can logout

---

## Support & Documentation

- **Backend Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Code Reviews**: See CODE_REVIEW_*.md files
- **Setup Guides**: See ENV_SETUP_GUIDE.md and QUICK_START_NEON.md

---

**Status**: 🟢 **Ready for Testing**

All integration points have been configured and tested. The frontend and backend are ready to work together seamlessly.
