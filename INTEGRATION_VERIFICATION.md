# Integration Verification Checklist

**Last Updated**: December 9, 2025
**Status**: Ready for Testing
**Purpose**: Verify that all components (backend, frontend, database, AI) are properly configured and working together

---

## Quick Status Check (2 minutes)

Run this before detailed testing to get a quick overview:

```bash
# Check backend is running
curl -s http://localhost:8000/health && echo "✅ Backend healthy" || echo "❌ Backend not running"

# Check frontend is accessible
curl -s http://localhost:3000 -o /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend not running"

# Check backend API docs
curl -s http://localhost:8000/docs -o /dev/null && echo "✅ API docs available" || echo "❌ API docs not available"
```

---

## Phase 1: Environment Configuration ✅

### 1.1 Backend Environment Variables

**Location**: `backend/.env`

**Required Variables**:
- [ ] `DATABASE_URL` - Neon PostgreSQL connection string
  - Format: `postgresql://[user]:[password]@[host]/[db]?sslmode=require`
  - Test: `echo $DATABASE_URL` should show full connection string

- [ ] `GEMINI_API_KEY` - Google Gemini API key
  - Format: `AIzaSy...` (starts with AIzaSy)
  - Test: `echo $GEMINI_API_KEY | cut -c1-10` should show `AIzaSyXXXX`

- [ ] `JWT_SECRET_KEY` - Cryptographically secure token
  - Format: 64-character hex string
  - Test: `echo $JWT_SECRET_KEY | wc -c` should output 65 (includes newline)

- [ ] `ALLOWED_ORIGINS` - CORS configuration
  - Should include: `http://localhost:3000` for frontend

**Verification**:
```bash
cd backend
# Load environment variables
export $(grep -v '^#' .env | xargs)

# Verify all required variables are set
echo "✓ DATABASE_URL: ${DATABASE_URL:0:20}..."
echo "✓ GEMINI_API_KEY: ${GEMINI_API_KEY:0:10}..."
echo "✓ JWT_SECRET_KEY: ${JWT_SECRET_KEY:0:10}..."
echo "✓ ALLOWED_ORIGINS: $ALLOWED_ORIGINS"
```

### 1.2 Frontend Environment Variables

**Location**: `frontend/.env.local`

**Required Variables**:
- [ ] `NEXT_PUBLIC_API_URL` - Backend API URL
  - Should be: `http://localhost:8000/api/v1`
  - Test: Check if set: `echo $NEXT_PUBLIC_API_URL`

- [ ] `NEXT_PUBLIC_APP_ENV` - Environment identifier
  - Should be: `development` for local testing

**Verification**:
```bash
cd frontend
# Check environment file
cat .env.local
# Should show:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
# NEXT_PUBLIC_APP_ENV=development
```

---

## Phase 2: Database Connectivity ✅

### 2.1 PostgreSQL Connection Test

**Test Connection String**:
```bash
# Test with psql if installed
psql "postgresql://[user]:[password]@[host]/[db]?sslmode=require" -c "SELECT NOW();"

# Alternative: Test from Python
cd backend
uv run python -c "
from app.database.session import check_db_connection
if check_db_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
"
```

**Success Criteria**:
- [ ] Connection returns timestamp without errors
- [ ] No SSL/TLS warnings
- [ ] Response time < 2 seconds

### 2.2 Database Schema Verification

**Check if migrations have run**:
```bash
cd backend
# Run migrations
uv run alembic upgrade head

# Verify tables exist
uv run python -c "
from app.database.session import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables created:', tables)
required = ['user', 'task']
missing = [t for t in required if t not in tables]
if missing:
    print('❌ Missing tables:', missing)
else:
    print('✅ All required tables exist')
"
```

**Success Criteria**:
- [ ] Tables `user` and `task` exist
- [ ] No migration errors
- [ ] Column definitions match schema

---

## Phase 3: Backend API Testing ✅

### 3.1 Health Endpoint

**Test**: Backend is running and database is accessible

```bash
curl -i http://localhost:8000/health
```

**Expected Response**:
```json
HTTP/1.1 200 OK
{"status":"healthy","database":"ok"}
```

**Success Criteria**:
- [ ] HTTP 200 status
- [ ] Returns JSON
- [ ] database field is "ok"

### 3.2 Authentication Flow

#### 3.2a Registration Endpoint

**Test**: Create a new user account

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "user-uuid",
  "email": "testuser@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-12-09T..."
}
```

**Success Criteria**:
- [ ] HTTP 201 Created
- [ ] Returns user object with ID
- [ ] is_active is true
- [ ] created_at is current timestamp

#### 3.2b Login Endpoint

**Test**: Get authentication token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Success Criteria**:
- [ ] HTTP 200 OK
- [ ] Returns access_token (starts with "eyJ")
- [ ] Token type is "bearer"
- [ ] expires_in is > 0

**Save Token**:
```bash
# Save token for next tests
export TOKEN="your_access_token_from_login"
```

### 3.3 Task Management Endpoints

#### 3.3a Create Task (with AI Analysis)

**Test**: Create a task and verify AI suggestions

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Review quarterly report",
    "description": "Analyze Q4 metrics and prepare executive summary",
    "priority": "high",
    "deadline": "2025-12-15"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": "task-uuid",
  "title": "Review quarterly report",
  "description": "Analyze Q4 metrics and prepare executive summary",
  "status": "pending",
  "priority": "high",
  "deadline": "2025-12-15",
  "ai_priority": "high",
  "estimated_duration": 3,
  "created_at": "2025-12-09T...",
  "updated_at": "2025-12-09T...",
  "user_id": "user-uuid"
}
```

**Success Criteria**:
- [ ] HTTP 201 Created
- [ ] Task created with provided fields
- [ ] **AI Fields Populated**:
  - [ ] `ai_priority` is set (not null)
  - [ ] `estimated_duration` is set (not null)
  - [ ] `ai_priority` value is valid: "low", "medium", "high", or "urgent"
  - [ ] `estimated_duration` is a positive integer

**If AI fields are null**, check:
- [ ] GEMINI_API_KEY is set correctly
- [ ] Backend logs show "Generated AI suggestions" message
- [ ] Check for "Error generating AI suggestions" in logs

#### 3.3b Get Tasks

**Test**: Retrieve all user's tasks

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/tasks
```

**Expected Response** (200 OK):
```json
[
  {
    "id": "task-uuid",
    "title": "Review quarterly report",
    "status": "pending",
    "priority": "high",
    "ai_priority": "high",
    "estimated_duration": 3,
    ...
  }
]
```

**Success Criteria**:
- [ ] HTTP 200 OK
- [ ] Returns array of tasks
- [ ] Includes newly created task

#### 3.3c Update Task

**Test**: Modify an existing task

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/task-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "in_progress",
    "priority": "urgent"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": "task-uuid",
  "title": "Review quarterly report",
  "status": "in_progress",
  "priority": "urgent",
  ...
}
```

**Success Criteria**:
- [ ] HTTP 200 OK
- [ ] Task fields updated correctly
- [ ] updated_at timestamp changed

#### 3.3d Complete Task

**Test**: Mark task as completed

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/task-uuid/complete \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (200 OK):
```json
{
  "id": "task-uuid",
  "title": "Review quarterly report",
  "status": "completed",
  ...
}
```

**Success Criteria**:
- [ ] HTTP 200 OK
- [ ] status is "completed"

#### 3.3e Delete Task

**Test**: Remove a task

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/task-uuid \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response** (204 No Content):
```
HTTP/1.1 204 No Content
```

**Success Criteria**:
- [ ] HTTP 204 No Content
- [ ] Task no longer appears in GET /tasks

---

## Phase 4: Frontend Integration ✅

### 4.1 Frontend Loads Successfully

**Test**: Open frontend in browser

```
http://localhost:3000
```

**Success Criteria**:
- [ ] Page loads without errors
- [ ] Homepage shows "Sign In" and "Create Account" buttons
- [ ] No console errors in browser DevTools

### 4.2 Registration Flow

**Test**: Create account through UI

1. [ ] Click "Create Account" button
2. [ ] Fill registration form:
   - Name: "Test User"
   - Email: "frontendtest@example.com"
   - Password: "SecurePass123" (12+ chars, uppercase, lowercase, number)
3. [ ] Click "Create Account"
4. [ ] Should redirect to dashboard

**Success Criteria**:
- [ ] Registration succeeds without errors
- [ ] Redirects to `/dashboard`
- [ ] Displays "Welcome, Test User"
- [ ] Network tab shows POST /api/v1/auth/register → 201
- [ ] Network tab shows POST /api/v1/auth/login → 200

### 4.3 Task Creation Flow

**Test**: Create a task through the UI

1. [ ] On dashboard, click "Create Task" or "+" button
2. [ ] Fill task form:
   - Title: "Test Integration Task"
   - Description: "Testing frontend-backend integration"
   - Priority: "high"
   - Deadline: Pick a date
3. [ ] Click "Create Task"
4. [ ] Task should appear in task list

**Success Criteria**:
- [ ] Task created successfully
- [ ] Task appears in task list immediately
- [ ] Network tab shows POST /api/v1/tasks → 201
- [ ] Response includes ai_priority and estimated_duration
- [ ] Task displays AI suggestions if populated

### 4.4 API Communication

**Browser DevTools Network Tab**:

```
POST /api/v1/auth/register    200 OK
POST /api/v1/auth/login       200 OK
GET  /api/v1/tasks            200 OK
POST /api/v1/tasks            201 Created
```

**Success Criteria**:
- [ ] All requests go to http://localhost:8000/api/v1
- [ ] No CORS errors
- [ ] All responses return correct status codes
- [ ] Authorization header includes Bearer token

### 4.5 Token Storage

**Browser DevTools Console**:

```javascript
// Check if token is stored
console.log(localStorage.getItem('accessToken'))
```

**Success Criteria**:
- [ ] Returns a token (starts with "eyJ")
- [ ] Token persists after page refresh

---

## Phase 5: AI Features ✅

### 5.1 Gemini API Connectivity

**Test**: Verify AI service can reach Gemini API

```bash
cd backend

# Test Gemini API directly
uv run python -c "
import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print('❌ GEMINI_API_KEY not set')
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content('Hello')
        print('✅ Gemini API working')
    except Exception as e:
        print(f'❌ Gemini API error: {e}')
"
```

**Success Criteria**:
- [ ] No authentication errors
- [ ] API responds within 2 seconds
- [ ] Response contains text

### 5.2 AI Priority Suggestions

**Test**: Create multiple tasks and verify AI suggestions vary

```bash
# Task 1: Simple task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Quick fix","priority":"medium"}' | grep -o '"ai_priority":"[^"]*"'

# Task 2: Complex task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Implement new feature with multiple integrations","priority":"high"}' | grep -o '"ai_priority":"[^"]*"'
```

**Success Criteria**:
- [ ] Both tasks return ai_priority values
- [ ] Values differ based on task complexity
- [ ] All values are valid: "low", "medium", "high", or "urgent"

### 5.3 AI Duration Estimation

**Test**: Verify duration estimates are reasonable

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Complete project documentation","description":"Write comprehensive API docs, user guides, and deployment instructions","priority":"high"}' \
  | grep -o '"estimated_duration":[0-9]*'
```

**Expected**: `estimated_duration` between 1-100 hours

**Success Criteria**:
- [ ] Duration estimate is a positive integer
- [ ] Estimate is reasonable for task complexity
- [ ] No negative numbers
- [ ] No null/undefined values

---

## Phase 6: Error Handling & Resilience ✅

### 6.1 Missing Authentication

**Test**: API rejects requests without token

```bash
curl -X GET http://localhost:8000/api/v1/tasks
```

**Expected Response** (401 Unauthorized):
```json
{"detail":"Not authenticated"}
```

**Success Criteria**:
- [ ] HTTP 401 status
- [ ] Error message is descriptive
- [ ] No sensitive information leaked

### 6.2 Invalid Token

**Test**: API rejects invalid tokens

```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer invalid.token.here"
```

**Expected Response** (401 Unauthorized):
```json
{"detail":"Invalid token"}
```

**Success Criteria**:
- [ ] HTTP 401 status
- [ ] Descriptive error message

### 6.3 Network Error Handling

**Test**: Frontend handles backend unavailability

1. [ ] Stop backend server
2. [ ] Try to create a task from frontend
3. [ ] Should show error message (not crash)

**Success Criteria**:
- [ ] Error message displays to user
- [ ] No console errors
- [ ] User can still interact with UI
- [ ] No blank screens

### 6.4 Graceful AI Degradation

**Test**: Tasks can be created if AI service is unavailable

1. [ ] Temporarily unset GEMINI_API_KEY
2. [ ] Create a task
3. [ ] Task should still be created

**Success Criteria**:
- [ ] Task created successfully
- [ ] ai_priority and estimated_duration are null
- [ ] No error to user
- [ ] Logs show "Gemini API key not configured"

---

## Phase 7: Performance Checks ✅

### 7.1 Backend Response Times

**Test**: Measure API response latencies

```bash
# Measure login response time
time curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }' > /dev/null
```

**Success Criteria**:
- [ ] Login: < 500ms
- [ ] Get tasks: < 200ms
- [ ] Create task (with AI): < 3 seconds
- [ ] Update task: < 500ms

### 7.2 Frontend Performance

**Test**: Check frontend loading time

1. [ ] Open Chrome DevTools → Network tab
2. [ ] Refresh http://localhost:3000
3. [ ] Check "Finish" time at bottom right

**Success Criteria**:
- [ ] Initial page load: < 3 seconds
- [ ] No hung requests
- [ ] All resources load successfully

### 7.3 Database Query Performance

**Test**: Verify no N+1 query problems

```bash
# Enable SQL logging temporarily
cd backend
export SQL_ECHO=true

# Run API request
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/tasks

# Count number of SQL queries in logs
# Should be minimal (< 3 queries for fetching tasks)
```

**Success Criteria**:
- [ ] No excessive queries for single endpoint
- [ ] Query execution time < 100ms total

---

## Phase 8: Security Verification ✅

### 8.1 CORS Configuration

**Test**: Verify CORS allows frontend, blocks other origins

```bash
# Request from allowed origin
curl -i -X OPTIONS http://localhost:8000/api/v1/auth/login \
  -H "Origin: http://localhost:3000"

# Should include: Access-Control-Allow-Origin: http://localhost:3000
```

**Success Criteria**:
- [ ] Frontend origin is allowed
- [ ] Response headers include CORS headers
- [ ] Unknown origins are rejected

### 8.2 JWT Token Security

**Test**: Verify tokens are secure

1. [ ] Login and get token
2. [ ] Check token in browser storage: `localStorage.getItem('accessToken')`
3. [ ] Copy token to https://jwt.io and decode
4. [ ] Verify:
   - [ ] Contains user ID
   - [ ] Contains expiration time
   - [ ] Secret is not exposed

**Success Criteria**:
- [ ] Token cannot be read by XSS (httpOnly would be better for production)
- [ ] Token has reasonable expiration (24 hours)
- [ ] Token contains user identification

### 8.3 Password Security

**Test**: Verify passwords are hashed

```bash
cd backend

# Check password hashing in database
uv run python -c "
from app.database.session import SessionLocal
from app.models.user import User
db = SessionLocal()
user = db.query(User).first()
if user and user.hashed_password.startswith('\$2b'):
    print('✅ Passwords are bcrypt hashed')
else:
    print('❌ Passwords not properly hashed')
"
```

**Success Criteria**:
- [ ] Passwords start with bcrypt prefix (\$2b)
- [ ] Passwords are not stored in plaintext
- [ ] Hashes are not reversible

### 8.4 Secrets Not in Logs

**Test**: Verify sensitive data is not logged

```bash
# Check backend logs for exposed secrets
cd backend
uv run uvicorn app.main:app --reload 2>&1 | grep -i "password\|key\|token" | head -5

# Should show no sensitive values, only configuration info
```

**Success Criteria**:
- [ ] No passwords in logs
- [ ] No API keys in logs
- [ ] No tokens in logs
- [ ] Only configuration names (not values) appear

---

## Troubleshooting Reference

| Issue | Solution |
|-------|----------|
| **❌ CORS errors** | Check ALLOWED_ORIGINS includes frontend URL |
| **❌ 401 Unauthorized** | Verify token is valid and not expired |
| **❌ ai_priority is null** | Check GEMINI_API_KEY is set, API key is valid |
| **❌ Database connection failed** | Verify DATABASE_URL is correct, SSL enabled |
| **❌ Frontend can't reach API** | Check NEXT_PUBLIC_API_URL is correct |
| **❌ Port already in use** | Change PORT in .env or kill existing process |
| **❌ Module not found** | Run `cd backend && uv sync` or `cd frontend && npm install` |

---

## Final Verification Checklist

### Before Declaring Ready for Production:

- [ ] All Phase 1-8 tests pass
- [ ] No console errors in browser DevTools
- [ ] No error logs in backend
- [ ] All API endpoints respond correctly
- [ ] AI features working (ai_priority and estimated_duration populated)
- [ ] Frontend communicates with backend successfully
- [ ] Authentication flows work (register, login, logout)
- [ ] CRUD operations work (create, read, update, delete tasks)
- [ ] Error handling is graceful
- [ ] Performance is acceptable
- [ ] Security checks pass

### Sign-Off

**Tested By**: ________________
**Date**: ________________
**Status**: [ ] ✅ Ready for Production [ ] ❌ Issues Found

---

## Next Steps

1. **Deploy to Staging**: Test with actual deployment tools
2. **Load Testing**: Verify performance under load
3. **Security Audit**: Professional security review
4. **User Acceptance Testing**: Real users test functionality
5. **Production Deployment**: Deploy to production environment

---

## Support

- **Backend API Docs**: http://localhost:8000/docs
- **Setup Guide**: `backend/ENV_SETUP_GUIDE.md`
- **Quick Start**: `QUICK_START_NEON.md`
- **Frontend-Backend Setup**: `FRONTEND_BACKEND_SETUP.md`
