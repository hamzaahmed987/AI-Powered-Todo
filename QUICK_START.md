# Quick Start - Todo Fullstack App

## 🚀 30 Second Setup

### Terminal 1: Backend
```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.simple_main:app --reload
```
✅ Backend running at http://localhost:8000

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend running at http://localhost:3000

### Terminal 3: Test
```bash
# Test API
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Test task"}'

# View all tasks
curl http://localhost:8000/api/tasks
```

**Done!** Open http://localhost:3000 in your browser

---

## 📁 What Was Created

### Backend Files
```
✨ NEW FILES CREATED:

app/models/simple_task.py          # SQLAlchemy Task model
app/schemas/simple_task.py         # Pydantic validation schemas
app/services/simple_task_service.py # Business logic
app/api/simple_tasks.py            # API routes (CRUD)
app/database/simple_session.py     # Database setup
app/simple_main.py                 # FastAPI app

📄 REFERENCE:
FULLSTACK_ARCHITECTURE.md          # Architecture documentation
CONVERSION_SUMMARY.md              # CLI → Fullstack conversion
SETUP_GUIDE.md                     # Detailed setup instructions
```

### Frontend Files
```
✨ NEW FILES CREATED:

src/lib/api.ts                     # Axios API client
src/lib/redux/store.ts             # Redux store config
src/lib/redux/hooks.ts             # Custom Redux hooks
src/lib/redux/slices/tasksSlice.ts # Tasks state & thunks
src/lib/redux/slices/uiSlice.ts    # UI state (modals)
src/components/providers/ReduxProvider.tsx # Redux wrapper

🔄 UPDATED:
app/layout.tsx                     # Added ReduxProvider
```

---

## 🎯 API Endpoints

### Quick Reference
```
✨ CREATE      POST   /api/tasks
📋 LIST        GET    /api/tasks
👀 VIEW        GET    /api/tasks/{id}
✏️  EDIT        PUT    /api/tasks/{id}
✅ COMPLETE    PATCH  /api/tasks/{id}/complete
🗑️  DELETE      DELETE /api/tasks/{id}
```

### Examples
```bash
# Create task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description":"Buy groceries"}'

# List all
curl http://localhost:8000/api/tasks

# Mark complete
curl -X PATCH http://localhost:8000/api/tasks/1/complete

# Update
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"description":"New description"}'

# Delete
curl -X DELETE http://localhost:8000/api/tasks/1
```

---

## 🔧 Available Tools

### Backend Tools
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Database
```bash
# Check database
sqlite3 backend/todo.db ".tables"
sqlite3 backend/todo.db "SELECT * FROM simple_tasks;"

# Reset (delete todo.db file)
rm backend/todo.db
```

---

## 📦 Tech Stack at a Glance

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend Framework | Next.js | 14+ |
| State Management | Redux Toolkit | 1.9+ |
| HTTP Client | Axios | 1.6+ |
| Backend Framework | FastAPI | 0.104+ |
| Database ORM | SQLAlchemy | 2.0+ |
| Database | SQLite | 3.x |
| Validation | Pydantic | 2.5+ |

---

## ⚡ Redux State

### Access in Components
```typescript
import { useAppSelector, useAppDispatch } from '@/lib/redux/hooks';
import { fetchTasks, addTask } from '@/lib/redux/slices/tasksSlice';

export function MyComponent() {
  const dispatch = useAppDispatch();
  const { items, loading } = useAppSelector(state => state.tasks);

  return (
    // component JSX
  );
}
```

### Redux Actions
```typescript
dispatch(fetchTasks())                    // Load tasks
dispatch(addTask("Buy milk"))             // Create task
dispatch(updateTask({id: 1, description: "Buy eggs"})) // Update
dispatch(completeTask(1))                 // Mark done
dispatch(deleteTask(1))                   // Delete
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Kill process or run on different port: `--port 8001` |
| Port 3000 in use | Run frontend on different port: `npm run dev -- -p 3001` |
| DB errors | Delete `backend/todo.db` and restart backend |
| API not responding | Check if backend is running: `curl http://localhost:8000/health` |
| Redux errors | Clear `.next` cache: `rm -rf frontend/.next` and restart |
| Module not found | Make sure virtual environment is activated in backend |

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **FULLSTACK_ARCHITECTURE.md** | System design & architecture |
| **CONVERSION_SUMMARY.md** | CLI → Fullstack conversion details |
| **SETUP_GUIDE.md** | Detailed step-by-step instructions |
| **QUICK_START.md** | This file - quick reference |

---

## ✅ Verification Checklist

- [ ] Backend running: `curl http://localhost:8000/health` → `{"status": "healthy"}`
- [ ] Frontend running: http://localhost:3000 loads in browser
- [ ] Can create task: `curl -X POST http://localhost:8000/api/tasks ...`
- [ ] Can list tasks: `curl http://localhost:8000/api/tasks`
- [ ] API docs loaded: http://localhost:8000/docs works
- [ ] Database created: `backend/todo.db` file exists

---

## 🚀 Next Steps

1. ✅ Verify everything is running (checklist above)
2. 🎨 Build UI components for:
   - Task form (add/edit)
   - Task list
   - Task item
   - Modal for details
3. 🔗 Connect components to Redux
4. 🎯 Test end-to-end functionality
5. 🚀 Deploy!

---

## 📞 Need Help?

1. **API Documentation**: Visit http://localhost:8000/docs
2. **Setup Issues**: See SETUP_GUIDE.md Troubleshooting section
3. **Architecture Questions**: See FULLSTACK_ARCHITECTURE.md
4. **Conversion Details**: See CONVERSION_SUMMARY.md

---

**Happy coding!** 🎉

For detailed instructions, see `SETUP_GUIDE.md`
