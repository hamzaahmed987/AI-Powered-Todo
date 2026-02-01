# Fullstack Todo App - Setup & Running Guide

## Overview

This document provides step-by-step instructions for running the converted fullstack todo application.

**What was created:**
- ✅ **Backend**: Simplified FastAPI application with SQLite database
- ✅ **Frontend**: Next.js 14+ with Redux Toolkit for state management
- ✅ **Documentation**: Architecture and setup guides

---

## Backend Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Step 1: Navigate to Backend Directory
```bash
cd "E:\Panaversity Hackathon\Todo App\backend"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env (optional - defaults are fine for local development)
# DATABASE_URL=sqlite:///./todo.db
# CORS_ORIGINS=http://localhost:3000
# DEBUG=True
```

### Step 5: Run Backend
```bash
# Using the simplified app
python -m uvicorn app.simple_main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Verify Backend is Running
```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "ok"
}
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Frontend Setup

### Prerequisites
- Node.js 18+ (LTS recommended)
- npm or yarn

### Step 1: Navigate to Frontend Directory
```bash
cd "E:\Panaversity Hackathon\Todo App\frontend"
```

### Step 2: Install Dependencies (if not already done)
```bash
npm install
# or
yarn install
```

### Step 3: Set Up Environment Variables
```bash
# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
EOF
```

### Step 4: Run Frontend Development Server
```bash
npm run dev
# or
yarn dev
```

**Expected Output:**
```
> next dev
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
```

### Verify Frontend is Running
Open your browser and navigate to: **http://localhost:3000**

---

## Running Both Together

### Terminal 1 - Backend
```bash
cd "E:\Panaversity Hackathon\Todo App\backend"
# Activate venv and run
python -m uvicorn app.simple_main:app --reload --port 8000
```

### Terminal 2 - Frontend
```bash
cd "E:\Panaversity Hackathon\Todo App\frontend"
npm run dev
```

### Terminal 3 - Testing (Optional)
```bash
# Test API endpoints
curl http://localhost:8000/api/tasks

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Buy groceries"}'
```

---

## File Structure Created

### Backend Files
```
backend/
├── app/
│   ├── models/
│   │   └── simple_task.py          # Task SQLAlchemy ORM model
│   ├── schemas/
│   │   └── simple_task.py          # Pydantic validation schemas
│   ├── services/
│   │   └── simple_task_service.py  # Business logic layer
│   ├── api/
│   │   └── simple_tasks.py         # API endpoints (CRUD routes)
│   ├── database/
│   │   └── simple_session.py       # Database configuration
│   └── simple_main.py              # FastAPI application setup
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variables example
```

### Frontend Files
```
frontend/
├── src/
│   ├── lib/
│   │   ├── api.ts                  # Axios API client
│   │   └── redux/
│   │       ├── store.ts            # Redux store configuration
│   │       ├── hooks.ts            # Custom Redux hooks
│   │       └── slices/
│   │           ├── tasksSlice.ts   # Tasks state & thunks
│   │           └── uiSlice.ts      # UI state (modals, etc)
│   └── components/
│       └── providers/
│           └── ReduxProvider.tsx   # Redux provider wrapper
├── app/
│   └── layout.tsx                  # Updated with ReduxProvider
└── .env.local                      # API URL configuration
```

---

## API Endpoints Reference

### Task Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/tasks` | Create new task |
| `GET` | `/api/tasks` | List all tasks with stats |
| `GET` | `/api/tasks/{id}` | Get single task details |
| `PUT` | `/api/tasks/{id}` | Update task description |
| `PATCH` | `/api/tasks/{id}/complete` | Mark task as complete |
| `DELETE` | `/api/tasks/{id}` | Delete task |

### Examples

**Create Task**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Learn Redux"}'
```

**List Tasks**
```bash
curl http://localhost:8000/api/tasks
```

**Complete Task**
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete
```

**Delete Task**
```bash
curl -X DELETE http://localhost:8000/api/tasks/1
```

---

## Redux State Structure

### Tasks State
```typescript
{
  tasks: {
    items: Task[],           // Array of tasks
    loading: boolean,        // Loading state
    error: string | null,    // Error message
    total: number,          // Total task count
    completed: number,      // Completed count
    pending: number        // Pending count
  },
  ui: {
    selectedTaskId: number | null,
    showModal: boolean,
    modalType: 'add' | 'edit' | 'details' | null,
    formError: string | null,
    editingId: number | null
  }
}
```

### Available Actions
**Tasks:**
- `fetchTasks()` - Load all tasks from API
- `addTask(description)` - Create new task
- `updateTask({id, description})` - Update task
- `completeTask(id)` - Mark complete
- `deleteTask(id)` - Delete task
- `clearError()` - Clear error message

**UI:**
- `openAddModal()` - Show add task modal
- `openEditModal(id)` - Show edit task modal
- `openDetailsModal(id)` - Show task details
- `closeModal()` - Hide modal
- `selectTask(id)` - Select task
- `setFormError(error)` - Set form error
- `clearFormError()` - Clear error

---

## Database Management

### Initialize Database
```bash
cd backend
python -c "from app.database.simple_session import init_db; init_db(); print('Database initialized!')"
```

### Check Database Schema
```bash
# View tables
sqlite3 todo.db ".tables"

# View tasks schema
sqlite3 todo.db ".schema simple_tasks"

# Query tasks
sqlite3 todo.db "SELECT * FROM simple_tasks;"
```

### Reset Database (Warning: Deletes All Data)
```bash
# Delete the database file
rm backend/todo.db

# Reinitialize
cd backend && python -c "from app.database.simple_session import init_db; init_db()"
```

---

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'app'"**
- Make sure you're in the `backend` directory
- Virtual environment should be activated

**"Address already in use" on port 8000**
```bash
# Find and kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

**Database errors**
- Delete `todo.db` and restart backend
- Backend will auto-recreate it on startup

### Frontend Issues

**"NEXT_PUBLIC_API_URL is not set"**
- Create `.env.local` file with API URL
- Restart development server

**Port 3000 already in use**
```bash
# Run on different port
npm run dev -- -p 3001
```

**Redux state not working**
- Check browser console for errors
- Verify ReduxProvider is in layout.tsx
- Clear .next cache: `rm -rf .next`

---

## Development Workflow

### Adding a New Feature

1. **Backend:**
   - Add model fields in `app/models/simple_task.py`
   - Update schemas in `app/schemas/simple_task.py`
   - Add service methods in `app/services/simple_task_service.py`
   - Add API routes in `app/api/simple_tasks.py`

2. **Frontend:**
   - Add API methods in `src/lib/api.ts`
   - Create async thunks in `src/lib/redux/slices/tasksSlice.ts`
   - Create components in `src/components/`
   - Use `useAppSelector` and `useAppDispatch` in components

### Testing

**Backend Unit Tests:**
```bash
cd backend
pytest tests/
```

**Manual API Testing:**
```bash
# Use Swagger UI: http://localhost:8000/docs
# Or curl commands from API reference above
```

**Frontend Testing:**
```bash
cd frontend
npm run test
# (if test setup exists)
```

---

## Production Deployment

### Backend (FastAPI)
```bash
# Use production server
pip install gunicorn
gunicorn app.simple_main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Or with Docker
docker build -f Dockerfile.backend -t todo-api .
docker run -p 8000:8000 todo-api
```

### Frontend (Next.js)
```bash
# Build for production
npm run build

# Start production server
npm run start

# Or deploy to Vercel
vercel deploy
```

### Database
- Replace SQLite with PostgreSQL for production
- Update `DATABASE_URL` to PostgreSQL connection string
- Run migrations with Alembic

---

## Key Features Implemented

✅ **Task CRUD Operations**
- Create, read, update, delete tasks
- Task completion status
- Timestamps (created_at)

✅ **Task Validation** (from original CLI)
- Description must be 1-200 characters
- Non-empty, whitespace-trimmed
- Same validation rules as CLI

✅ **Task Statistics**
- Total task count
- Completed vs pending counts
- Real-time updates on list view

✅ **Redux State Management**
- Centralized task state
- UI state (modals, selected tasks)
- Async thunks for API calls
- Error handling and loading states

✅ **API Integration**
- Axios client with interceptors
- Error handling with user feedback
- Base URL configuration via env vars

---

## Next Steps

### To Add Components:
1. Create form component for adding/editing tasks
2. Create task list component
3. Create task item component
4. Create modal/dialog for details

### To Enhance:
- Add task categories/tags
- Add due dates
- Add task priority
- Add real-time updates (WebSockets)
- Add user authentication
- Add task sharing

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redux Toolkit Documentation](https://redux-toolkit.js.org/)
- [Next.js Documentation](https://nextjs.org/docs)
- [SQLAlchemy ORM Documentation](https://docs.sqlalchemy.org/en/20/orm/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation at `/docs` (backend)
3. Check browser console for frontend errors
4. Review Redux DevTools in browser

---

**Last Updated:** December 9, 2025
