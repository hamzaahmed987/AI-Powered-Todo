# Fullstack Todo App Architecture Plan

## Executive Summary
Convert the existing Python CLI Todo app into a complete fullstack web application using:
- **Backend**: FastAPI (Python) - RESTful API
- **Frontend**: Next.js 14+ (React/TypeScript) - Modern SPA with Redux for state management
- **Database**: SQLite/PostgreSQL (for persistence instead of in-memory)

---

## 1. Current State Analysis

### Existing CLI App Structure
```
src/todo_cli/
├── models.py       # Task dataclass with validation
├── store.py        # In-memory TaskStore (CRUD operations)
├── commands.py     # Business logic layer
├── cli.py          # Interactive REPL interface
├── main.py         # Entry point
└── __main__.py     # CLI launcher
```

### Current Features
- ✓ Add tasks
- ✓ List all tasks with status/count
- ✓ View single task details
- ✓ Mark tasks as complete
- ✓ Update task descriptions
- ✓ Delete tasks
- ✓ Built-in validation (non-empty, max 200 chars)

---

## 2. Proposed Fullstack Architecture

### High-Level Flow
```
[Next.js Frontend] <--REST API--> [FastAPI Backend] <--ORM--> [SQLite/PostgreSQL]
   (React/Redux)                   (Pydantic models)            (Persistent DB)
```

### Directory Structure
```
todo-app/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # FastAPI app setup
│   │   ├── models.py          # Pydantic models (Task)
│   │   ├── database.py        # Database configuration
│   │   ├── schemas.py         # Request/Response schemas
│   │   ├── api/
│   │   │   └── routes.py      # API endpoints
│   │   └── services/
│   │       └── task_service.py # Business logic (adapted from CLI)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables
│   └── docker-compose.yml      # Optional: Docker setup
│
├── frontend/                   # Next.js application
│   ├── app/
│   │   ├── layout.tsx          # Root layout with Redux provider
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── providers/
│   │   │   └── ReduxProvider.tsx
│   │   ├── TaskForm.tsx        # Add/Update task form
│   │   ├── TaskList.tsx        # Display tasks
│   │   ├── TaskItem.tsx        # Individual task
│   │   └── TaskDetail.tsx      # Task details modal
│   ├── lib/
│   │   ├── api.ts              # API client functions
│   │   └── redux/
│   │       ├── store.ts        # Redux store setup
│   │       ├── slices/
│   │       │   ├── tasksSlice.ts    # Tasks reducer
│   │       │   └── uiSlice.ts       # UI state (modals, etc)
│   │       └── hooks.ts         # Custom Redux hooks
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.local               # Environment variables
│
└── docker-compose.yml          # Orchestrate both services
```

---

## 3. Backend Specification (FastAPI)

### 3.1 Dependencies
```
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.0
python-dotenv==1.0.0
cors  # Enable CORS for frontend
```

### 3.2 Data Model (Pydantic)
```python
# Mirrors existing Task model but with persistence
class Task(BaseModel):
    id: int
    description: str  # 1-200 chars
    completed: bool = False
    created_at: datetime
    updated_at: datetime = None
```

### 3.3 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/tasks` | Create new task |
| `GET` | `/api/tasks` | List all tasks |
| `GET` | `/api/tasks/{id}` | Get single task |
| `PUT` | `/api/tasks/{id}` | Update task description |
| `PATCH` | `/api/tasks/{id}/complete` | Mark task as complete |
| `DELETE` | `/api/tasks/{id}` | Delete task |

### 3.4 Request/Response Examples

**Create Task**
```json
// POST /api/tasks
{
  "description": "Buy groceries"
}

// Response (201 Created)
{
  "id": 1,
  "description": "Buy groceries",
  "completed": false,
  "created_at": "2025-12-09T10:00:00Z",
  "updated_at": "2025-12-09T10:00:00Z"
}
```

**List Tasks**
```json
// GET /api/tasks
// Response (200 OK)
{
  "tasks": [
    {"id": 1, "description": "Buy groceries", "completed": false, ...},
    {"id": 2, "description": "Clean house", "completed": true, ...}
  ],
  "total": 2,
  "completed": 1,
  "pending": 1
}
```

### 3.5 Error Handling
- `400 Bad Request` - Validation error (empty description, too long)
- `404 Not Found` - Task ID doesn't exist
- `500 Internal Server Error` - Unexpected error

---

## 4. Frontend Specification (Next.js + Redux)

### 4.1 Dependencies
```json
{
  "@reduxjs/toolkit": "^1.9.0",
  "react-redux": "^8.1.0",
  "axios": "^1.6.0",
  "typescript": "^5.0"
}
```

### 4.2 Redux State Structure
```typescript
// Tasks Slice
{
  tasks: {
    items: Task[],
    loading: boolean,
    error: string | null
  },
  ui: {
    selectedTaskId: number | null,
    showModal: boolean,
    modalType: 'add' | 'edit' | 'details',
    formError: string | null
  }
}
```

### 4.3 Redux Actions (via createSlice)

**tasksSlice.ts**
- `fetchTasks()` - Load all tasks from API
- `addTask(description)` - Create new task
- `updateTask(id, description)` - Update task
- `completeTask(id)` - Mark task complete
- `deleteTask(id)` - Delete task

**uiSlice.ts**
- `openModal(type)` - Show add/edit modal
- `closeModal()` - Hide modal
- `selectTask(id)` - Select task for viewing
- `setFormError(error)` - Set form error message

### 4.4 Component Structure

**Layout Structure**
```tsx
<ReduxProvider>
  <Layout>
    <Header />
    <TaskForm /> {/* Add new task */}
    <TaskStats /> {/* Total/Done/Pending counts */}
    <TaskList>
      {tasks.map(task => <TaskItem key={task.id} task={task} />)}
    </TaskList>
    <TaskDetailModal /> {/* Modal for viewing details */}
  </Layout>
</ReduxProvider>
```

### 4.5 Key Features

**Task Form Component**
- Input field for task description (max 200 chars)
- Character counter
- Submit button
- Error display
- Clear on success

**Task List Component**
- Display all tasks in table format
- Show completion status with visual indicator
- Display creation date
- Action buttons (Complete, Edit, Delete, View)

**Task Item Component**
- Checkbox to toggle completion
- Task description with truncation
- Quick action buttons
- Confirm delete dialog

---

## 5. Integration Points

### 5.1 API Client (lib/api.ts)
```typescript
// Wrapper around axios for API calls
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
})

export const taskApi = {
  getTasks: () => api.get('/tasks'),
  createTask: (description) => api.post('/tasks', { description }),
  updateTask: (id, description) => api.put(`/tasks/${id}`, { description }),
  completeTask: (id) => api.patch(`/tasks/${id}/complete`),
  deleteTask: (id) => api.delete(`/tasks/${id}`)
}
```

### 5.2 Redux Async Thunks
```typescript
export const fetchTasks = createAsyncThunk(
  'tasks/fetchTasks',
  async () => {
    const response = await taskApi.getTasks()
    return response.data.tasks
  }
)
```

---

## 6. Database Design

### Option A: SQLite (Development/Demo)
- Single file: `todo.db`
- No setup required
- Good for prototyping
- Limited to single process

### Option B: PostgreSQL (Production-Ready)
- Scalable
- Multi-user support
- Backup/restore capabilities
- Requires docker or external server

### Schema
```sql
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  description VARCHAR(200) NOT NULL,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 7. Development Workflow

### Phase 1: Backend Setup ✓
- [ ] Initialize FastAPI project
- [ ] Create Pydantic models
- [ ] Setup SQLAlchemy ORM
- [ ] Implement API routes (CRUD)
- [ ] Add input validation
- [ ] Test endpoints (Postman/curl)

### Phase 2: Frontend Setup ✓
- [ ] Initialize Next.js project
- [ ] Install Redux dependencies
- [ ] Create Redux store and slices
- [ ] Create API client
- [ ] Setup ReduxProvider

### Phase 3: Components ✓
- [ ] Create TaskForm component
- [ ] Create TaskList component
- [ ] Create TaskItem component
- [ ] Create TaskDetailModal
- [ ] Wire up Redux actions

### Phase 4: Integration ✓
- [ ] Connect frontend to backend API
- [ ] Test CRUD operations end-to-end
- [ ] Handle error cases
- [ ] Add loading states

### Phase 5: Polish ✓
- [ ] Add animations/transitions
- [ ] Improve UI/UX
- [ ] Add dark mode (optional)
- [ ] Optimize performance

---

## 8. Running the Application

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App available at http://localhost:3000
```

### Docker (Optional)
```bash
docker-compose up
```

---

## 9. Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./todo.db
CORS_ORIGINS=http://localhost:3000
DEBUG=True
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## 10. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI over Flask** | Built-in async, auto-docs, Pydantic validation |
| **Redux over Context API** | Predictable state management, DevTools, middleware support |
| **SQLAlchemy ORM** | Type-safe, migration support, multiple DB backends |
| **Separate backend/frontend** | Independent deployment, clear separation of concerns |
| **Reuse CLI business logic** | Validation rules remain consistent |

---

## 11. Migration from CLI

### What Stays the Same
- Task validation rules (1-200 chars, non-empty)
- Business logic (mark complete, update, delete)
- Data structure (id, description, completed, created_at)

### What Changes
- Storage: In-memory → Persistent database
- Interface: CLI REPL → Web UI
- State management: Local store → Redux
- Communication: Direct calls → HTTP API

---

## 12. Future Enhancements

- [ ] User authentication & multi-user support
- [ ] Task categories/tags
- [ ] Due dates
- [ ] Task priority levels
- [ ] Recurring tasks
- [ ] Export/Import functionality
- [ ] Mobile app (React Native)
- [ ] Real-time updates (WebSockets)

