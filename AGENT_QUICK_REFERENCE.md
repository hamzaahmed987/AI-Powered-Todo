# OpenAI Agents SDK - Quick Reference Guide

## 🚀 Quick Start

### Base URL
```
http://localhost:8000/api/v1/agent
```

### Authentication
All requests require Bearer token:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## 📝 API Endpoints

### 1. Chat with Agent (Main Endpoint)
```
POST /api/v1/agent/chat
Content-Type: application/json
Authorization: Bearer TOKEN

{
  "message": "Your task management request"
}
```

**Response:**
```json
{
  "message": "Agent's response",
  "success": true,
  "action_taken": "Description of what was done"
}
```

### 2. Get Capabilities
```
GET /api/v1/agent/capabilities
Authorization: Bearer TOKEN
```

**Response:**
```json
{
  "agent_name": "Task Manager Assistant",
  "capabilities": [
    {
      "action": "Create tasks",
      "description": "...",
      "examples": [...]
    },
    ...
  ],
  "supported_statuses": ["pending", "in_progress", "completed"],
  "supported_priorities": ["low", "medium", "high", "urgent"]
}
```

## 💬 Natural Language Examples

### CREATE Tasks
```
"Add a task called Buy groceries"
"Create a new task: Finish project report due tomorrow"
"Make a task for Prepare presentation with urgent priority"
"Add Meeting prep with deadline next Friday"
"Create 'Learn React' as a low priority task"
```

### UPDATE Tasks
```
"Mark my project task as completed"
"Update the deadline for Meeting prep to next Friday"
"Change Buy groceries priority from medium to high"
"Move task status to in_progress for the presentation"
"Update the description of my Shopping task"
```

### DELETE Tasks
```
"Delete the old task from yesterday"
"Remove the completed Shopping task"
"Delete my outdated tasks"
"Remove the task called Old project"
```

### RETRIEVE Info
```
"Show me details of my project task"
"What's the deadline for Meeting prep?"
"Tell me about the Shopping task"
"Get information about my urgent tasks"
```

## 🎯 Common Workflows

### Workflow 1: Create and Update Task
```
User: "Add a task called Workout with high priority"
Agent: ✅ Task created successfully

User: "Change it to completed"
Agent: ✅ Task marked as completed
```

### Workflow 2: Create Task with Deadline
```
User: "Create a task for Report due tomorrow with urgent priority"
Agent: ✅ Task created with deadline set to tomorrow
```

### Workflow 3: Task Management Flow
```
User: "Create groceries task with medium priority"
Agent: ✅ Task created

User: "Show me the details"
Agent: ✅ Returns: Status=pending, Priority=medium, etc.

User: "Mark it as in_progress"
Agent: ✅ Task status updated

User: "Delete it"
Agent: ✅ Task deleted
```

## 📅 Date/Time Format

Use ISO 8601 format:
- With time: `2025-12-25T10:30:00`
- With timezone: `2025-12-25T10:30:00Z`

**Or use natural language:**
- "tomorrow"
- "next Friday"
- "in 3 days"
- "Monday 3 PM"

## 🏷️ Priority Levels

| Priority | Use Case |
|----------|----------|
| `low` | Can wait, not urgent |
| `medium` | Normal priority (default) |
| `high` | Important, should do soon |
| `urgent` | Critical, do immediately |

## 📊 Task Status

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `in_progress` | Currently being worked on |
| `completed` | Finished |

## ❌ Error Messages & Solutions

| Error | Solution |
|-------|----------|
| "Invalid task ID format" | Use the actual task ID from creation response |
| "Invalid priority: X" | Use one of: low, medium, high, urgent |
| "Invalid status: X" | Use one of: pending, in_progress, completed |
| "Task not found" | Task doesn't exist or belongs to another user |
| "Invalid deadline format" | Use ISO 8601 (e.g., 2025-12-25T10:30:00) |

## 🔐 Security

- ✅ All requests authenticated with JWT token
- ✅ Users can only access/modify their own tasks
- ✅ Database session automatically scoped to user
- ✅ All inputs validated before processing
- ✅ Operations logged for audit trail

## 📊 Response Examples

### Success Response
```json
{
  "message": "Task 'Buy groceries' created successfully with high priority",
  "success": true,
  "action_taken": "Agent processed your request and executed any necessary task operations"
}
```

### Error Response
```json
{
  "message": "Task 'Setup meeting' updated successfully: status to 'completed'",
  "success": false,
  "action_taken": "Task update failed due to validation error"
}
```

## 🛠️ Tools Available

| Tool | Function | Example |
|------|----------|---------|
| `add_task` | Create new tasks | "Add a task called ..." |
| `update_task` | Modify tasks | "Update my task to ..." |
| `delete_task` | Remove tasks | "Delete the task ..." |
| `get_task_info` | Retrieve details | "Show me details of ..." |

## 📱 Frontend Integration

```typescript
// Call agent endpoint
const response = await fetch('/api/v1/agent/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userInput
  }),
});

const data = await response.json();
console.log(data.message); // Display to user
```

## ⚡ Tips & Tricks

### ✅ DO
- Use natural, conversational language
- Include specific details like priority and deadline
- Ask for confirmation before deleting
- Use agent capabilities endpoint to see examples

### ❌ DON'T
- Don't worry about exact format - agent understands natural language
- Don't use task names with special characters
- Don't create tasks with empty titles
- Don't use future dates beyond reasonable bounds

## 🎓 Learning Resources

1. **View API Documentation**: `http://localhost:8000/docs` (Swagger UI)
2. **Get Agent Capabilities**: `GET /api/v1/agent/capabilities`
3. **Try Examples**: Use the examples above as templates
4. **Check Response**: Always validate `success` field in response

## 🆘 Troubleshooting

### Agent not responding
- ✅ Check authentication token is valid
- ✅ Verify endpoint URL is correct
- ✅ Check backend server is running

### Task not created
- ✅ Ensure you provided a task title
- ✅ Check priority value (low/medium/high/urgent)
- ✅ Verify date format if deadline provided

### Can't see my tasks
- ✅ Confirm you're logged in with correct user
- ✅ Agent only shows tasks created by current user
- ✅ Tasks are stored in database, not in agent memory

## 📞 Support

For issues or questions:
1. Check error message in response
2. Review this quick reference
3. Check full documentation in `OPENAI_AGENTS_INTEGRATION.md`
4. Review agent setup in `AGENT_SETUP_SUMMARY.md`

---

**Ready to use!** Start sending messages to the agent and it will help manage your tasks through natural conversation. 🚀
