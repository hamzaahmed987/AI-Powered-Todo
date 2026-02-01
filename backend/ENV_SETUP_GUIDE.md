# Environment Variables Setup Guide

Complete step-by-step guide to obtaining and configuring all required environment variables for the AI-Powered Todo App backend.

**Table of Contents**
- [1. Neon PostgreSQL Database](#1-neon-postgresql-database)
- [2. OpenAI API Key](#2-openai-api-key)
- [3. JWT Secret Key](#3-jwt-secret-key)
- [4. Complete .env File Example](#4-complete-env-file-example)
- [5. Verification Steps](#5-verification-steps)
- [6. Troubleshooting](#6-troubleshooting)
- [7. Security Checklist](#7-security-checklist)

---

## 1. Neon PostgreSQL Database

Neon is a serverless PostgreSQL platform that provides a free tier perfect for development and small applications.

### Step 1: Create Neon Account

1. Go to **[https://neon.tech](https://neon.tech)**
2. Click **"Sign Up"** button (top right)
3. Sign up using one of:
   - GitHub account (recommended - fastest)
   - Google account
   - Email address
4. Verify your email if required
5. You'll be redirected to the Neon Console dashboard

### Step 2: Create a New Project

Once logged in to Neon Console:

1. Click **"Create Project"** button
2. Fill in project details:
   - **Project Name**: `todo-app` (or your preferred name)
   - **Region**: Choose the region closest to your location or users
     - Examples: `us-east-2`, `eu-central-1`, `ap-south-1`
   - **PostgreSQL Version**: Select version 15 or 16 (recommended)
3. Click **"Create Project"** button
4. Wait 30-60 seconds for the project to be created

### Step 3: Get Connection String

After project creation, you'll see the project dashboard:

1. Look for **"Connection Details"** section on the dashboard
2. You should see your connection string displayed:
   ```
   postgresql://alex:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```
3. **IMPORTANT**: Copy the entire connection string to your clipboard
4. You'll paste this into `DATABASE_URL` in your `.env` file

### Step 4: Connection String Breakdown

Understanding the Neon connection string format:

```
postgresql://[USERNAME]:[PASSWORD]@[HOSTNAME]/[DATABASE]?sslmode=require
           └─────┬─────┘ └────┬────┘ └────────┬────────┘ └───┬───┘ └─────┬─────┘
              User Info   Password        Neon Host       Database SSL Mode
```

**Components:**
- **Protocol**: `postgresql://` (standard PostgreSQL protocol)
- **USERNAME**: Auto-generated user (e.g., `neondb_owner`, `alex`)
  - This is your database user for authentication
- **PASSWORD**: Auto-generated secure password
  - Do not change this unless necessary
  - If you forget it, you can reset it in Neon Console
- **HOSTNAME**: Your Neon endpoint (e.g., `ep-cool-darkness-123456.us-east-2.aws.neon.tech`)
  - This uniquely identifies your Neon server
  - Includes region information
- **DATABASE**: Database name (usually `neondb` or your project name)
  - You can create multiple databases if needed
- **?sslmode=require**: SSL encryption requirement
  - **IMPORTANT**: This is mandatory for Neon - never remove it
  - Ensures your connection is encrypted

### Step 5: Set DATABASE_URL in .env

Create or edit `backend/.env` file:

```bash
# Copy the entire connection string from Step 3
DATABASE_URL=postgresql://YOUR_USERNAME:YOUR_PASSWORD@YOUR_HOSTNAME/YOUR_DATABASE?sslmode=require
```

**Example with real values:**
```bash
DATABASE_URL=postgresql://neondb_owner:npg_9x8Y7w6V5u4t3s2r@ep-cool-darkness-123456.us-east-2.aws.neon.tech/todo_app?sslmode=require
```

### Optional: Create Custom Database

If you want a specific database name:

1. In Neon Console, click **"SQL Editor"** on the left sidebar
2. Run this SQL command:
   ```sql
   CREATE DATABASE todo_app;
   ```
3. Update your connection string to use `todo_app`:
   ```bash
   DATABASE_URL=postgresql://...@.../todo_app?sslmode=require
   ```

### Free Tier Limits

Neon's free tier includes:
- **Storage**: 0.5 GB (sufficient for development)
- **Compute**: Shared
- **Connections**: Up to 20 concurrent connections
- **No cost**: Completely free (no credit card required)

---

## 2. Google Gemini API Key

Google's Gemini API powers intelligent task analysis. The free tier is completely free - no payment needed!

### Step 1: Access Google AI Studio

1. Go to **[https://aistudio.google.com](https://aistudio.google.com)**
2. Sign in with your **Google account**
   - Any Google account works (Gmail, Google Workspace, etc.)
   - If you don't have one, create one for free
3. Accept the terms of service if prompted

### Step 2: Create API Key

1. Click on **"Get API key"** in the left sidebar
2. Or go directly to: **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**
3. Click the **"Create API key"** button
4. You'll see two options:
   - **Create API key in new project** (recommended for most users)
   - **Create API key in existing project** (if you have a Google Cloud project)
5. Click **"Create API key in new project"**
6. Your API key will be generated immediately

### Step 3: Copy Your API Key

1. The key will be displayed in format: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
2. Click the **copy button** next to the key
3. **IMPORTANT**: Store this key securely
   - You can view it anytime from AI Studio
   - It won't be shown again until you create a new one

### Step 4: Set GEMINI_API_KEY in .env

```bash
# Paste your key from Step 3
GEMINI_API_KEY=AIzaSyYOUR_ACTUAL_KEY_HERE
```

**Example with real format:**
```bash
GEMINI_API_KEY=AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIj
```

### Free Tier Details

**Model Used**: Gemini 2.0 Flash (optimized for speed and efficiency)

**Free Tier Limits**:
- **1500 requests per day** (plenty for development and small production apps)
- **60 requests per minute**
- **1 million tokens per minute**
- **100 RPM per user**
- **Cost**: **100% FREE**

**Sufficient For**:
- Development and testing
- Small to medium production applications
- Up to ~1,500 task analyses per day

### Paid Tier (Optional)

If you exceed free tier limits, you can enable billing:

1. Set up billing in Google Cloud Console
2. **Pricing** (as of 2024):
   - **Input**: ~$0.075 per 1M tokens
   - **Output**: ~$0.30 per 1M tokens
3. **Cost per Task Suggestion**: ~$0.00001 per request (extremely cheap)
4. **Typical monthly cost**: Less than $1 even with high usage
5. Set up budget alerts to stay informed

### Gemini vs OpenAI Comparison

| Feature | Gemini 2.0 Flash (Free) | OpenAI GPT-4o-mini (Paid) |
|---------|------------------------|---------------------------|
| Cost | **FREE** (1500 req/day) | $0.15 per 1M input tokens |
| Speed | ~1-2 seconds | ~1-3 seconds |
| Quality | Excellent task analysis | Excellent task analysis |
| Setup | No payment required | Requires $5-10 minimum |
| Daily Limit | 1500 requests/day | Usage-based billing |
| Best For | Development & production | High-volume production |

**Recommendation**: Gemini 2.0 Flash is perfect for this Todo App - fast, free, and high quality!

### Managing API Keys

- **Never share your API key** with anyone
- **Never commit API keys** to Git (they're in .gitignore)
- **Rotate keys periodically** (every 3-6 months)
- **Revoke old keys** if compromised:
  1. Go to https://aistudio.google.com/app/apikey
  2. Click the trash icon next to the key
  3. Generate a new one

---

## 3. JWT Secret Key

JWT (JSON Web Tokens) secure your API endpoints. The secret key signs tokens to prevent tampering.

### Step 1: Generate Secure Secret Key

You must generate a cryptographically secure random key. Never use a simple password.

**Option A: Using OpenSSL (Recommended)**

```bash
openssl rand -hex 32
```

**Output example:**
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

**Option B: Using Python**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Or with uv (since this project uses uv):

```bash
uv run python -c "import secrets; print(secrets.token_hex(32))"
```

**Option C: Using Node.js**

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Option D: Online Generator (Less Secure)**

Visit **[https://www.random.org/bytes/](https://www.random.org/bytes/)**
- Set size to 32
- Set format to Hexadecimal
- Copy the generated value

### Step 2: Set JWT_SECRET_KEY in .env

```bash
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
```

### Security Best Practices

- **Never use simple passwords**: Always use cryptographically generated keys
- **Use different keys for different environments**:
  - Development key can be less sensitive
  - Production key must be highly secure
  - Staging key separate from both
- **Rotate keys periodically**: Every 3-6 months in production
- **Never commit keys to Git**: Only commit `.env.example`
- **Use strong key length**: At least 32 bytes (the command above generates this)
- **If compromised**: Generate a new key immediately

### Token Expiration Settings

The `.env` file includes related settings:

```bash
# Access token lifetime (shorter = more secure but user logs out sooner)
JWT_EXPIRATION_HOURS=24

# Refresh token lifetime (longer = user stays logged in longer)
REFRESH_TOKEN_EXPIRATION_DAYS=7
```

**Current settings** (recommended for most apps):
- Users stay logged in for 24 hours
- After 24 hours, they need to log in again
- Or refresh token lasts 7 days (implementation for future)

---

## 4. Complete .env File Example

Create `backend/.env` with all variables. Use the values obtained from sections 1-3 above.

```bash
# =============================================================================
# Backend Environment Variables
# =============================================================================

# Database - Neon Serverless PostgreSQL
# Get from Neon Console (see Section 1 above)
# Format: postgresql://[user]:[password]@[hostname]/[database]?sslmode=require
DATABASE_URL=postgresql://neondb_owner:npg_AbCdEfGh123456@ep-cool-darkness-123456.us-east-2.aws.neon.tech/todo_app?sslmode=require

# OpenAI Configuration
# Get from OpenAI API Keys page (see Section 2 above)
# Format: sk-proj-...
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

# JWT & Authentication
# Generate with: openssl rand -hex 32 (see Section 3 above)
# Must be at least 64 characters
JWT_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=7

# Server Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS & Security (allow frontend origins)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# AI Feature Configuration
AI_TIMEOUT_SECONDS=3
AI_RATE_LIMIT_CALLS=10
AI_RATE_LIMIT_WINDOW=60

# Optional: SQL Query Logging (for debugging)
SQL_ECHO=false
```

### Frontend .env Setup

Also create `frontend/.env.local` (separate from backend):

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Application Environment
NEXT_PUBLIC_APP_ENV=development
NEXT_PUBLIC_APP_NAME=AI Todo App
```

---

## 5. Verification Steps

After setting up your `.env` file, verify everything works:

### Step 1: Verify Files Exist

```bash
# Check backend .env
ls -la backend/.env

# Check frontend .env.local
ls -la frontend/.env.local
```

### Step 2: Test Database Connection

```bash
cd backend
uv run python -c "from app.database.session import check_db_connection; print('✓ Database connected' if check_db_connection() else '✗ Connection failed')"
```

**Expected output:**
```
✓ Database connected
```

**If it fails:**
- Check DATABASE_URL is correct
- Verify Neon project is not paused
- Confirm password doesn't contain special chars (URL encode if needed)

### Step 3: Test OpenAI API

```bash
uv run python -c "
from openai import OpenAI
client = OpenAI()
print('✓ OpenAI API connected')
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'say hello'}],
    max_tokens=10
)
print('✓ API working correctly')
"
```

**Expected output:**
```
✓ OpenAI API connected
✓ API working correctly
```

**If it fails:**
- Check API key is correct
- Verify payment method is added to OpenAI account
- Ensure free trial account has been upgraded

### Step 4: Run Database Migrations

```bash
cd backend
uv run alembic upgrade head
```

**Expected output:**
```
INFO [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO [alembic.runtime.migration] Will assume transactional DDL.
INFO [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, done
```

### Step 5: Start Backend Server

```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Verify it's working:**
- Open browser: http://localhost:8000/docs
- You should see Swagger API documentation
- Try the health check endpoint

### Step 6: Test Health Endpoint

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status": "healthy", "database": "connected"}
```

---

## 6. Troubleshooting

### Database Connection Issues

**Error: `connection refused`**
```
Error: connection refused / Connection refused
```

**Solutions:**
1. Verify DATABASE_URL is correct (copy-paste from Neon Console)
2. Check if Neon project is paused (free tier pauses after inactivity):
   - Go to https://console.neon.tech
   - Click your project
   - Click "Resume" if needed
3. Verify no extra spaces in `.env` file
4. Test connectivity:
   ```bash
   psql "your-connection-string"
   ```

**Error: `SSL required`**
```
Error: FATAL:  ssl/tls required / sslmode=disable not supported
```

**Solutions:**
1. Ensure `?sslmode=require` is in your DATABASE_URL
2. The parameter must be at the very end
3. Don't modify or remove `sslmode`

**Error: `authentication failed`**
```
Error: FATAL: password authentication failed for user "neondb_owner"
```

**Solutions:**
1. Copy connection string directly from Neon Console (don't retype)
2. If password contains special characters, verify they're preserved
3. Check if credentials in Neon Console have changed:
   - Go to https://console.neon.tech
   - Verify username and password shown there
4. Reset password if needed (Neon Console → Settings)

### OpenAI API Issues

**Error: `invalid API key`**
```
Error: Incorrect API key provided
```

**Solutions:**
1. Verify key format starts with `sk-proj-` or `sk-`
2. Check for trailing spaces in .env file
3. Ensure you copied the entire key (not truncated)
4. Regenerate key if needed:
   - Go to https://platform.openai.com/api-keys
   - Delete old key
   - Create new key
   - Copy immediately and paste into .env

**Error: `insufficient credits`**
```
Error: You exceeded your current quota
```

**Solutions:**
1. Add payment method to OpenAI account
2. Go to https://platform.openai.com/account/billing
3. Click "Add payment method"
4. Wait 5-10 minutes for system to update
5. Try request again

**Error: `API not available in your region`**
```
Error: Access denied in your region/country
```

**Solutions:**
- OpenAI restricts access in some countries
- Use a VPN or contact OpenAI support

### JWT Issues

**Error: `invalid token`**
```
Error: Could not validate credentials / Invalid token
```

**Solutions:**
1. Check JWT_SECRET_KEY is set correctly
2. JWT_SECRET_KEY must be at least 32 characters (64 hex digits)
3. Don't change JWT_SECRET_KEY after issuing tokens (breaks all existing tokens)
4. In development, it's OK to change and re-login

### Port Already in Use

**Error: `Port 8000 is already in use`**
```
Error: [Errno 48] Address already in use
```

**Solutions:**
1. Find process using port 8000:
   ```bash
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```
2. Kill the process or use different port:
   ```bash
   PORT=8001 uv run uvicorn app.main:app
   ```

### Module Import Errors

**Error: `No module named 'openai'`**
```
ModuleNotFoundError: No module named 'openai'
```

**Solutions:**
1. Install backend dependencies:
   ```bash
   cd backend
   uv sync
   ```
2. Verify you're in the right directory (backend/)
3. Verify uv is installed:
   ```bash
   uv --version
   ```

---

## 7. Security Checklist

Before deploying to production, verify:

### .env File Security
- [ ] `.env` file is in `.gitignore` (not committed to Git)
- [ ] `.env` file has correct permissions (readable only by owner)
  ```bash
  chmod 600 .env  # Unix/Linux/macOS
  ```
- [ ] No `.env` files ever committed to Git history

### Credentials & Keys
- [ ] JWT_SECRET_KEY is cryptographically generated (64+ hex chars)
- [ ] JWT_SECRET_KEY is different for production vs development
- [ ] OPENAI_API_KEY is valid and has usage limits set
- [ ] DATABASE_URL uses sslmode=require
- [ ] DATABASE_URL password is strong and unique

### API Keys Management
- [ ] OpenAI usage limits configured ($5-10/month recommended)
- [ ] OpenAI account has two-factor authentication enabled
- [ ] API keys are rotated every 3-6 months
- [ ] Old API keys are revoked/deleted
- [ ] Team members have individual API keys (not shared)

### Database Security
- [ ] Neon database password is strong
- [ ] Database user has minimal required permissions
- [ ] Backup strategy is in place
- [ ] Database connections use SSL/TLS

### Environment-Specific
- [ ] ENVIRONMENT is set correctly (development/production)
- [ ] DEBUG=false in production (never true in prod)
- [ ] LOG_LEVEL is appropriate (INFO in prod)
- [ ] ALLOWED_ORIGINS doesn't include wildcards in production

### Access Control
- [ ] Only authorized team members have `.env` file access
- [ ] Secrets are never logged or printed
- [ ] No secrets in error messages
- [ ] Monitoring/alerting for failed auth attempts

---

## Need Help?

**Official Documentation:**
- Neon: https://neon.tech/docs
- OpenAI: https://platform.openai.com/docs
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org

**Quick Links:**
- Neon Console: https://console.neon.tech
- OpenAI Platform: https://platform.openai.com
- OpenAI API Keys: https://platform.openai.com/api-keys
- OpenAI Billing: https://platform.openai.com/account/billing

**Project Help:**
- GitHub Issues: Create an issue in the repository
- Documentation: Check `QUICK_START_NEON.md` for quick setup guide
- Code Issues: Review `backend/ENV_SETUP_GUIDE.md` (this file)

---

**Last Updated**: December 2024
**Tested With**: Python 3.11+, uv (latest), FastAPI 0.104.1, Neon (latest)
