# 🧪 Testing Guide - Gemini + OpenAI Agents Integration

**Status**: Ready for testing
**Backend**: http://localhost:8000
**Documentation**: http://localhost:8000/docs

---

## ⚡ Quick Test (2 minutes)

### Step 1: Open Swagger UI
```
http://localhost:8000/docs
```

### Step 2: Check Agent Capabilities
1. Click on `GET /api/v1/agent/capabilities`
2. Click "Try it out"
3. Click "Execute"

**Expected**: Returns list of agent capabilities (no auth required for this endpoint)

```json
{
  "agent_name": "Task Manager Assistant",
  "capabilities": [
    {
      "action": "Create tasks",
      "description": "Create new tasks...",
      "examples": [...]
    },
    ...
  ]
}
```

### Step 3: Test Agent Chat (Requires Authentication)
To test `/api/v1/agent/chat`, you need a valid JWT token.

**Option A: Get token via login endpoint**
1. Click on `POST /auth/login`
2. Click "Try it out"
3. Enter test credentials:
```json
{
  "email": "test@example.com",
  "password": "your_password"
}
```
4. Copy the `access_token` from response

**Option B: Use existing token**
If you have a valid JWT token, skip to Step 4.

### Step 4: Send Message to Agent
1. Click on `POST /api/v1/agent/chat`
2. Click "Try it out"
3. Click the lock icon 🔒 to authorize
4. Paste your JWT token
5. In request body, enter:
```json
{
  "message": "Add a task called Buy groceries with high priority"
}
```
6. Click "Execute"

**Expected Response**:
```json
{
  "message": "Task 'Buy groceries' created successfully with high priority",
  "success": true,
  "action_taken": "Created task using add_task tool"
}
```

---

## 📝 Test Cases

### Test 1: Create Task
**Request**:
```json
{
  "message": "Add a task called Review code changes with medium priority and deadline tomorrow"
}
```

**Expected**: Task created in database with specified title, priority, and deadline

---

### Test 2: Update Task
**Request**:
```json
{
  "message": "Mark my Buy groceries task as completed"
}
```

**Expected**: Task status changed to "completed" in database

---

### Test 3: Delete Task
**Request**:
```json
{
  "message": "Delete the Review code task"
}
```

**Expected**: Task removed from database

---

### Test 4: Get Task Info
**Request**:
```json
{
  "message": "Show me details of my Buy groceries task"
}
```

**Expected**: Agent returns task details (title, status, priority, deadline)

---

## 🔍 Verification Points

### Backend Logs
Check the backend terminal for log entries like:
```
INFO - Agent chat from user test@example.com: Add a task called...
INFO - Agent processed message from test@example.com
```

### Database Verification
Verify tasks are created/updated in the database:
```sql
-- Connect to your database and run:
SELECT * FROM tasks WHERE user_id = 'your-user-id' ORDER BY created_at DESC;
```

### Network Traffic
Use browser DevTools to verify:
1. Request sent to `POST /api/v1/agent/chat`
2. Response status: `200 OK`
3. Response time: Usually 1-3 seconds

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Get valid JWT token first |
| 500 Internal Server Error | Check backend logs for agent errors |
| Agent timeout | Check GOOGLE_API_KEY is set correctly |
| Database error | Verify database connection in backend logs |

---

## 📊 Performance Expectations

- **First response**: ~1-2 seconds (cold start)
- **Subsequent responses**: ~500ms - 1.5 seconds
- **Tool execution**: Depends on database, usually <100ms

---

## ✅ Success Criteria

Your integration is working if:

✅ Backend runs without `DefaultCredentialsError`
✅ `/api/v1/agent/chat` returns 200 OK responses
✅ Agent creates/updates/deletes tasks in database
✅ Agent provides natural language responses
✅ ChatBot frontend can send messages and receive responses

---

## 🚀 Next: Test with Frontend

Once backend testing is complete:

```bash
# In frontend directory:
npm run dev

# Visit: http://localhost:3000
# Open ChatBot widget
# Send: "Add a task called Test with high priority"
# Verify task is created and response appears in chat
```

---

**Ready?** Open http://localhost:8000/docs and start testing! 🎉

