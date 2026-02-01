# Email Validation API Testing Guide

## ✅ Backend Routes Implemented

### 1. `/api/v1/auth/check-email` - Email Checker (NEW)
**Method:** `GET`
**Purpose:** Check if email exists (for login/register validation)

**Request:**
```bash
curl "http://localhost:8000/api/v1/auth/check-email?email=test@example.com"
```

**Response:**
```json
{
  "exists": false,
  "message": "Email is available"
}
```

or

```json
{
  "exists": true,
  "message": "Email is already registered"
}
```

---

### 2. `/api/v1/auth/login` - Login (UPDATED)
**Method:** `POST`
**Purpose:** Login with specific error messages

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "wrongpassword"}'
```

**Possible Responses:**

**Success (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Email not found (404):**
```json
{
  "detail": "Email not found. Please check your email or sign up."
}
```

**Wrong password (401):**
```json
{
  "detail": "Incorrect password. Please try again."
}
```

**Account disabled (403):**
```json
{
  "detail": "Account is disabled. Please contact support."
}
```

---

### 3. `/api/v1/auth/register` - Register (UPDATED)
**Method:** `POST`
**Purpose:** Register with detailed password validation

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'
```

**Possible Responses:**

**Success (201):**
```json
{
  "user": {
    "id": "uuid...",
    "email": "newuser@example.com",
    "full_name": "Test User"
  },
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Email already exists (409):**
```json
{
  "detail": "Email already registered. Please login instead."
}
```

**Password too short (400):**
```json
{
  "detail": "Password must be at least 12 characters long"
}
```

**Missing uppercase (400):**
```json
{
  "detail": "Password must contain at least one uppercase letter"
}
```

**Missing lowercase (400):**
```json
{
  "detail": "Password must contain at least one lowercase letter"
}
```

**Missing number (400):**
```json
{
  "detail": "Password must contain at least one number"
}
```

---

## Testing Steps

### 1. Start Backend Server
```bash
cd /home/noman-khan/Desktop/mobile/backend
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Email Checker

**Test with non-existent email:**
```bash
curl "http://localhost:8000/api/v1/auth/check-email?email=nonexistent@test.com"
```
Expected: `{"exists": false, "message": "Email is available"}`

**Test with existing email (after registration):**
```bash
curl "http://localhost:8000/api/v1/auth/check-email?email=test@example.com"
```
Expected: `{"exists": true, "message": "Email is already registered"}`

### 3. Test Registration

**Register a new user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
```

**Try to register same email again:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "AnotherPass123",
    "full_name": "Another User"
  }'
```
Expected: `{"detail": "Email already registered. Please login instead."}`

**Try weak password:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "weak@example.com",
    "password": "short",
    "full_name": "Weak Pass"
  }'
```
Expected: `{"detail": "Password must be at least 12 characters long"}`

### 4. Test Login

**Login with correct credentials:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```
Expected: Returns access_token

**Login with non-existent email:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "notexist@example.com",
    "password": "SomePassword123"
  }'
```
Expected: `{"detail": "Email not found. Please check your email or sign up."}`

**Login with wrong password:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "WrongPassword123"
  }'
```
Expected: `{"detail": "Incorrect password. Please try again."}`

---

## Frontend Integration Verification

Your mobile app should now:

1. ✅ **Login Screen:**
   - Show "⚠️ Email not registered" when user types unregistered email
   - Show "❌ Incorrect password" when login fails with wrong password
   - Auto-clear errors when user starts typing

2. ✅ **Register Screen:**
   - Show "⚠️ Email already registered" when user types existing email
   - Show "✓ Email available" when email is unique
   - Show specific password errors (length, uppercase, lowercase, number)
   - Auto-clear errors when user starts typing

3. ✅ **Debouncing:**
   - Wait 800ms after user stops typing before checking email
   - Show loading spinner during check
   - No API spam (only 1 call per email check)

---

## Troubleshooting

### Issue: "Method Not Allowed" error
**Solution:** Make sure backend server is running and CORS is configured

### Issue: Email check not working
**Solution:**
1. Check backend logs for errors
2. Verify database connection
3. Test endpoint directly with curl

### Issue: Frontend not getting proper errors
**Solution:**
1. Check browser/mobile console for error messages
2. Verify apiService.ts is parsing errors correctly
3. Check that error.message or error.detail is being read

---

## API Documentation

Once backend is running, view full API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
