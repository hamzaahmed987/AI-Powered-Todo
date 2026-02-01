# AI-Powered Todo Application - API Documentation

## Overview

The AI-Powered Todo application is a full-stack web application that combines a FastAPI backend with a Next.js frontend to provide an intelligent task management solution. The application features AI-powered task analysis, natural language processing, and real-time collaboration capabilities.

## Architecture

### Backend Architecture
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based with python-jose
- **AI Integration**: OpenAI Agents SDK with OpenRouter compatibility
- **Caching**: Custom in-memory caching with TTL
- **Logging**: Structured logging with JSON support

### Frontend Architecture
- **Framework**: Next.js 16 with App Router
- **State Management**: Redux Toolkit with RTK Query
- **UI Components**: React with Tailwind CSS
- **API Client**: Axios with interceptors
- **Forms**: Formik with Yup validation

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### POST /api/v1/auth/login
Authenticate a user and retrieve access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### GET /api/v1/auth/me
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true
}
```

### Task Management Endpoints

#### GET /api/v1/tasks
Retrieve a paginated list of user's tasks with optional filtering.

**Query Parameters:**
- `status`: Filter by task status (pending, in_progress, completed)
- `priority`: Filter by task priority (low, medium, high, urgent)
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 20, max: 100)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": "uuid",
        "title": "Task Title",
        "description": "Task Description",
        "status": "pending",
        "priority": "medium",
        "deadline": "2024-12-31T23:59:59Z",
        "estimated_duration": 60,
        "ai_priority": "high",
        "ai_estimated_duration": 90,
        "owner_id": "uuid",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "completed_at": null
      }
    ],
    "total": 1,
    "skip": 0,
    "limit": 20
  }
}
```

#### POST /api/v1/tasks
Create a new task.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "deadline": "2024-12-31T23:59:59Z",
  "estimated_duration": 60
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "New Task",
    "description": "Task description",
    "status": "pending",
    "priority": "medium",
    "deadline": "2024-12-31T23:59:59Z",
    "estimated_duration": 60,
    "ai_priority": null,
    "ai_estimated_duration": null,
    "owner_id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "completed_at": null
  }
}
```

#### GET /api/v1/tasks/{task_id}
Retrieve a specific task.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Task Title",
    "description": "Task Description",
    "status": "pending",
    "priority": "medium",
    "deadline": "2024-12-31T23:59:59Z",
    "estimated_duration": 60,
    "ai_priority": "high",
    "ai_estimated_duration": 90,
    "owner_id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "completed_at": null
  }
}
```

#### PUT /api/v1/tasks/{task_id}
Update a specific task.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Updated Task Title",
  "status": "in_progress",
  "priority": "high"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "title": "Updated Task Title",
    "description": "Task Description",
    "status": "in_progress",
    "priority": "high",
    "deadline": "2024-12-31T23:59:59Z",
    "estimated_duration": 60,
    "ai_priority": "high",
    "ai_estimated_duration": 90,
    "owner_id": "uuid",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "completed_at": null
  }
}
```

#### DELETE /api/v1/tasks/{task_id}
Delete a specific task.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
- Status: 204 No Content

### AI Agent Endpoints

#### POST /api/v1/agent/chat
Send a message to the AI task management agent.

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Create a task called 'Buy groceries' with high priority"
}
```

**Response:**
```json
{
  "message": "Task 'Buy groceries' created successfully with high priority. AI suggests duration: 45 minutes.",
  "success": true,
  "action": "create",
  "task_data": {
    "id": "uuid",
    "title": "Buy groceries",
    "status": "pending",
    "priority": "high"
  }
}
```

#### GET /api/v1/agent/capabilities
Get information about the agent's capabilities.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "agent_name": "Task Manager",
  "capabilities": [
    {
      "action": "Create tasks",
      "description": "Add new tasks with title, description, priority, and deadline",
      "example": "Create a task called 'Buy groceries' with high priority"
    },
    {
      "action": "Update tasks",
      "description": "Change task title, status, priority, or deadline",
      "example": "Mark my project task as completed"
    },
    {
      "action": "Delete tasks",
      "description": "Remove tasks you no longer need",
      "example": "Delete the old task from yesterday"
    },
    {
      "action": "Get task info",
      "description": "Retrieve detailed information about a task",
      "example": "Show me the details of my project task"
    }
  ],
  "statuses": ["pending", "in_progress", "completed"],
  "priorities": ["low", "medium", "high", "urgent"]
}
```

## Application Architecture

### Backend Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration and settings
│   ├── dependencies.py         # Dependency injection
│   ├── middleware/             # Custom middleware
│   │   └── request_logger.py
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── task.py
│   │   └── base.py
│   ├── schemas/                # Pydantic validation schemas
│   ├── api/                    # API route handlers
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── agent.py
│   ├── services/               # Business logic layer
│   │   ├── user_service.py
│   │   ├── task_service.py
│   │   └── ai_service.py
│   ├── database/               # Database session and migrations
│   │   └── session.py
│   ├── agents/                 # AI agent implementations
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools.py
│   │   ├── openrouter_client.py
│   │   └── gemini_client.py
│   └── utils/                  # Utilities and helpers
│       ├── logger.py
│       ├── cache.py
│       ├── performance.py
│       ├── exceptions.py
│       └── response.py
├── tests/                      # Test files
│   ├── conftest.py
│   ├── test_auth_api.py
│   ├── test_task_api.py
│   ├── test_agent_api.py
│   ├── test_performance.py
│   └── test_ai_service.py
├── requirements.txt
└── pyproject.toml
```

### Frontend Structure
```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── auth/
│   │   ├── page.tsx
│   │   └── components/
│   └── dashboard/
│       ├── page.tsx
│       └── components/
│           ├── TaskList.tsx
│           ├── TaskItem.tsx
│           └── TaskForm.tsx
├── components/
│   ├── providers/
│   ├── AuthModal.tsx
│   ├── ChatBot.tsx
│   ├── FormField.tsx
│   ├── LoginModal.tsx
│   ├── NewTaskModal.tsx
│   └── SignupModal.tsx
├── src/
│   ├── hooks/
│   │   └── useTasks.ts
│   ├── lib/
│   │   └── validations.ts
│   ├── redux/
│   │   ├── store.ts
│   │   ├── hooks.ts
│   │   ├── slices/
│   │   │   └── taskSlice.ts
│   │   └── thunks/
│   │       └── taskThunks.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── tasksService.ts
│   │   └── agentService.ts
│   ├── types/
│   │   └── errors.ts
│   └── utils/
│       └── toastUtils.ts
├── public/
├── package.json
├── tsconfig.json
└── next.config.ts
```

## AI Features

### Task Analysis
The application uses AI to analyze task descriptions and provide:
- Priority suggestions based on urgency and complexity
- Estimated duration for task completion
- Productivity insights and recommendations

### Natural Language Processing
The AI agent understands natural language commands such as:
- "Create a task called 'Buy groceries' with high priority"
- "Mark my project task as completed"
- "Delete the old task from yesterday"
- "Show me details of my project task"

### Intelligent Task Management
- Automatic priority assignment based on content analysis
- Duration estimation for better time management
- Contextual suggestions for task organization
- Productivity insights based on task patterns

## Security Features

### Authentication
- JWT-based authentication with refresh tokens
- Secure password hashing with bcrypt
- Input validation and sanitization
- Rate limiting for authentication endpoints

### Authorization
- Role-based access control
- Task ownership verification
- Secure API endpoint protection
- Proper session management

## Performance Optimizations

### Caching
- In-memory caching with TTL for frequently accessed data
- Automatic cache invalidation on data updates
- Optimized database queries with proper indexing

### Monitoring
- Structured logging with JSON format
- Request/response time tracking
- Database operation monitoring
- AI interaction logging
- Performance metric collection

## Error Handling

### Backend Error Handling
- Custom exception classes with appropriate HTTP status codes
- Structured error responses with machine-readable codes
- Comprehensive validation at API boundaries
- Graceful degradation for AI service failures

### Frontend Error Handling
- User-friendly error messages
- Toast notifications for different error types
- Form validation with real-time feedback
- Network error handling with retry mechanisms

## Deployment

The application is designed for containerized deployment with Docker and supports scaling across multiple instances. Environment variables control configuration for different deployment environments.

## Technologies Used

### Backend
- FastAPI: Modern Python web framework
- SQLAlchemy: Python SQL toolkit and ORM
- PostgreSQL: Relational database
- OpenAI Agents SDK: AI agent framework
- uvicorn: ASGI server

### Frontend
- Next.js: React framework
- React: UI library
- Redux Toolkit: State management
- Tailwind CSS: Utility-first CSS framework
- TypeScript: Type-safe JavaScript