# Quickstart: Development Environment Setup

**Feature**: 002-fullstack-ai-todo | **Created**: 2025-12-08

This guide gets you from zero to running the fullstack application locally.

---

## Prerequisites

- **Git**: For version control
- **Docker & Docker Compose**: For PostgreSQL and local development environment
- **Python 3.11+**: For backend development
- **Node.js 18+**: For frontend development
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys (required for AI features)

**Verify installations**:
```bash
git --version
docker --version
python --version
node --version
npm --version
```

---

## Project Structure Quick Reference

```
project-root/
├── backend/          # FastAPI server
├── frontend/         # Next.js application
├── docker-compose.yml # Local dev environment
└── specs/            # Feature specifications & docs
    └── 002-fullstack-ai-todo/
        ├── spec.md           # Requirements
        ├── plan.md           # Architecture
        ├── data-model.md     # Database schema
        ├── research.md       # Design decisions
        ├── contracts/        # API contracts
        └── quickstart.md     # This file
```

---

## Step 1: Clone & Setup Repository

```bash
# Clone the repository
git clone <repository-url>
cd Todo\ App

# Create feature branch (if not already on 002-fullstack-ai-todo)
git checkout 002-fullstack-ai-todo

# Verify you're on correct branch
git branch --show-current
```

---

## Step 2: Start PostgreSQL

The application requires PostgreSQL 14+. Use Docker Compose for local development.

```bash
# Start PostgreSQL and optional services
docker-compose up -d postgres

# Verify PostgreSQL is running
docker-compose ps

# Check logs (optional)
docker-compose logs postgres
```

**Connection Details** (from docker-compose.yml):
- Host: `localhost`
- Port: `5432`
- Database: `todo_app`
- User: `postgres`
- Password: `postgres` (development only!)

---

## Step 3: Setup Backend

### 3.1 Navigate to backend directory

```bash
cd backend
```

### 3.2 Create Python virtual environment

```bash
# Option A: Using venv (built-in)
python -m venv venv

# Option B: Using uv (faster, recommended)
uv sync

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 3.3 Install dependencies

```bash
# If using pip/venv
pip install -r requirements.txt

# If using uv
uv sync  # Already done above
```

### 3.4 Setup environment variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local with your values
# CRITICAL: Add your OpenAI API key
nano .env.local  # or use your preferred editor
```

**Required environment variables**:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/todo_app

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-...

# JWT
JWT_SECRET_KEY=<generate-with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=7

# Server
DEBUG=false
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Generate JWT secret**:
```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3.5 Run database migrations

```bash
# Initialize migrations (first time only)
alembic init migrations  # Should already exist

# Run all pending migrations
alembic upgrade head

# Check migration status
alembic current
```

**Verify database**:
```bash
# Connect to PostgreSQL
psql -h localhost -U postgres -d todo_app

# List tables (should see users, tasks tables)
\dt

# Exit PostgreSQL
\q
```

### 3.6 Start backend server

```bash
# Run FastAPI with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Application will be available at:
# http://localhost:8000
# API docs at: http://localhost:8000/docs (Swagger UI)
# Alternative docs: http://localhost:8000/redoc (ReDoc)
```

**Verify backend is running**:
```bash
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy"}
```

---

## Step 4: Setup Frontend

### 4.1 Navigate to frontend directory

```bash
cd ../frontend  # From project root
```

### 4.2 Install Node dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 4.3 Setup environment variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**Required environment variables**:
```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Optional: Analytics, monitoring
NEXT_PUBLIC_APP_ENV=development
```

### 4.4 Start frontend development server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev

# Application will be available at:
# http://localhost:3000
```

**Verify frontend is running**:
- Open http://localhost:3000 in your browser
- Should see login/register page
- If not, check console for errors

---

## Step 5: Test the Application

### 5.1 Create a test user

```bash
# Option A: Via API
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "full_name": "Test User"
  }'

# Option B: Via frontend
# Visit http://localhost:3000/auth/register
# Fill in email, password, name
# Click "Register"
```

### 5.2 Login

```bash
# Option A: Via API
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Response will include access_token

# Option B: Via frontend
# Visit http://localhost:3000/auth/login
# Enter email and password
# Click "Login"
```

### 5.3 Create a task

```bash
# Option A: Via frontend
# Dashboard should load automatically after login
# Click "New Task" button
# Enter: "Review quarterly reports by Friday"
# Click "Create"
# System should generate AI priority/duration estimates

# Option B: Via API
TOKEN="<access_token from login>"
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review quarterly reports by Friday",
    "description": "Analyze Q4 performance metrics and prepare summary"
  }'
```

### 5.4 Get tasks

```bash
# List all tasks for authenticated user
TOKEN="<access_token>"
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

## Step 6: Run Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_models.py

# Run tests matching pattern
pytest -k "test_create_task"

# Watch mode (re-run on file changes)
pytest-watch
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific test file
npm test -- TaskForm.test.tsx
```

---

## Step 7: Verify API Documentation

Once backend is running, API documentation is auto-generated:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI spec**: http://localhost:8000/openapi.json

---

## Troubleshooting

### PostgreSQL Connection Error

**Problem**: `psycopg2.OperationalError: connection failed`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# If not, start it
docker-compose up -d postgres

# Check logs
docker-compose logs postgres

# Verify connection details in .env.local
# Default: postgresql://postgres:postgres@localhost:5432/todo_app
```

### OpenAI API Errors

**Problem**: `openai.error.AuthenticationError: No API key provided`

**Solution**:
```bash
# Check API key is in .env.local
echo $OPENAI_API_KEY

# If empty, set it:
export OPENAI_API_KEY=sk-your-actual-key-here

# Restart backend server
# Note: Task CRUD should still work even without OpenAI (graceful degradation)
```

### Frontend Can't Connect to Backend

**Problem**: "Failed to fetch" errors in browser console

**Solution**:
```bash
# Verify backend is running on port 8000
curl http://localhost:8000/health

# Check NEXT_PUBLIC_API_URL in frontend/.env.local
# Should be: http://localhost:8000/api/v1

# Restart frontend server after updating .env
npm run dev
```

### Port Already in Use

**Problem**: `Address already in use :8000` or `:3000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process (replace PID)
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different ports in .env
```

---

## Development Workflow

### Making changes to backend

```bash
cd backend

# Edit code (server auto-reloads)
# Run tests
pytest

# Check types
mypy app/

# Format code
black app/

# Lint
flake8 app/
```

### Making changes to frontend

```bash
cd frontend

# Edit code (server auto-reloads)
# Run tests
npm test

# Type check
npm run type-check

# Format/lint
npm run lint
npm run format
```

### Database changes

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Add status field to tasks"

# Review generated migration in migrations/versions/

# Apply migration
alembic upgrade head

# Revert if needed
alembic downgrade -1
```

---

## Useful Commands Reference

### Backend

```bash
cd backend

# Uvicorn server
uvicorn app.main:app --reload

# Database migrations
alembic upgrade head         # Apply pending migrations
alembic downgrade -1         # Revert last migration
alembic current              # Show current revision

# Testing
pytest                       # Run all tests
pytest --cov=app tests/     # With coverage
pytest -k "test_name"       # Specific test

# Type checking & linting
mypy app/                    # Type check
black app/                   # Auto-format
flake8 app/                  # Lint
```

### Frontend

```bash
cd frontend

# Development
npm run dev                  # Start dev server
npm run build                # Build for production
npm start                    # Run production build

# Testing
npm test                     # Jest test runner
npm test -- --coverage      # With coverage

# Code quality
npm run type-check          # TypeScript check
npm run lint                # ESLint
npm run format              # Prettier
```

### Docker

```bash
# Start services
docker-compose up -d postgres

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres

# Clean up (delete volumes)
docker-compose down -v
```

---

## Next Steps

1. **Explore the codebase**: Review `backend/app/` and `frontend/src/`
2. **Run tests**: `pytest` and `npm test` to ensure everything works
3. **Create tasks**: Use the UI or API to create test tasks
4. **Test AI features**: Watch task creation generate priority/duration automatically
5. **Review specs**: Check `specs/002-fullstack-ai-todo/` for detailed requirements

---

## Getting Help

- **API Docs**: http://localhost:8000/docs (when backend running)
- **Spec**: `specs/002-fullstack-ai-todo/spec.md`
- **Architecture**: `specs/002-fullstack-ai-todo/plan.md`
- **Database**: `specs/002-fullstack-ai-todo/data-model.md`
- **API Contracts**: `specs/002-fullstack-ai-todo/contracts/openapi.yaml`

---

**Happy coding! 🚀**
