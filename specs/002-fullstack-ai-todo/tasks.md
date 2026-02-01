# Tasks: Fullstack AI-Powered Todo App

**Input**: Design documents from `/specs/002-fullstack-ai-todo/`
**Tech Stack**: Next.js (Frontend) | FastAPI (Backend) | PostgreSQL | OpenAI Agents SDK
**Branch**: `002-fullstack-ai-todo`

**Organization**: Tasks are grouped by phase (Setup → Foundational → User Stories → Polish) with user stories organized by priority (P1, P2, P3).

**MVP Strategy**: Deploy P1 first; P2 and P3 are enhancements. Each user story is independently testable.

---

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Tasks marked can run in parallel (different files/modules, no dependencies)
- **[Story]**: User story label (US1, US2, US3) required for story-specific tasks
- **File paths**: Exact files to create/modify for LLM implementation

---

## Phase 1: Setup (Shared Infrastructure & Project Initialization)

**Purpose**: Create project structure and initialize both frontend and backend scaffolding

**⏱️ Estimated Duration**: 1-2 hours
**Blocking**: All other phases depend on this

### Backend Setup

- [x] T001 Create backend directory structure per plan.md in `backend/app/` with subdirectories: models, schemas, api, services, database, utils
- [x] T002 [P] Create `backend/pyproject.toml` with dependencies: FastAPI, SQLAlchemy, Pydantic, psycopg2-binary, alembic, python-jose, passlib, bcrypt, pytest, httpx, openai
- [x] T003 [P] Create `backend/requirements.txt` with pinned dependency versions
- [x] T004 [P] Create `backend/.env.example` with environment variables: DATABASE_URL, OPENAI_API_KEY, JWT_SECRET_KEY, DEBUG, ALLOWED_ORIGINS
- [x] T005 [P] Create `backend/README.md` with project description and development instructions

### Frontend Setup

- [x] T006 Create `frontend/package.json` with dependencies: next, react, typescript, tailwindcss, axios, zustand, jest, @testing-library/react
- [x] T007 [P] Create `frontend/.env.example` with NEXT_PUBLIC_API_URL variable
- [x] T008 [P] Create `frontend/tsconfig.json` with strict TypeScript configuration
- [x] T009 [P] Create `frontend/tailwind.config.js` for TailwindCSS setup
- [x] T010 [P] Create `frontend/next.config.js` with Next.js configuration
- [x] T011 [P] Create `frontend/jest.config.js` and `frontend/jest.setup.js` for testing
- [x] T012 [P] Create `frontend/README.md` with project description and development instructions

### Docker & Development Environment

- [x] T013 Create/update `docker-compose.yml` to run PostgreSQL 14 locally with exposed port 5432, default credentials (postgres:postgres)
- [x] T014 [P] Create root `.env.example` with all required environment variables for both backend and frontend

**Checkpoint**: Project structure initialized, dependencies configured, ready for foundational infrastructure

---

## Phase 2: Foundational (Blocking Prerequisites for All User Stories)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until Phase 2 is complete

### Database & Migration Setup

- [x] T015 Initialize Alembic in `backend/app/database/migrations/` with configuration for PostgreSQL
- [x] T016 Create `backend/app/database/session.py` with SQLAlchemy engine, SessionLocal, Base class, and connection pooling configuration
- [x] T017 [P] Create `backend/app/database/migrations/versions/001_initial_schema.py` migration with:
  - users table (id, email, password_hash, full_name, created_at, updated_at, is_active)
  - tasks table (id, owner_id FK, title, description, status, priority, deadline, estimated_duration, created_at, updated_at, completed_at)
  - Proper indexes (user_email, task_owner_id, task_status, composite idx_task_owner_status)
  - Foreign key constraints with CASCADE delete from users → tasks

### Authentication & Authorization Framework

- [x] T018 Create `backend/app/services/auth_service.py` with:
  - `hash_password()` using bcrypt via passlib
  - `verify_password()` for authentication
  - `create_access_token()` with JWT encoding (algorithm: HS256, 15 min expiration)
  - `create_refresh_token()` with JWT encoding (7 day expiration)
  - `verify_token()` for JWT validation
  - Uses configuration from environment variables (JWT_SECRET_KEY, JWT_ALGORITHM)

- [x] T019 Create `backend/app/dependencies.py` with:
  - `get_db()` session dependency for FastAPI
  - `get_current_user()` dependency for authenticated endpoints (parses JWT, returns User object)
  - `get_optional_user()` for public endpoints that may have auth context

- [x] T020 [P] Create `backend/app/utils/exceptions.py` with custom exception classes:
  - `InvalidCredentialsError` (401)
  - `ForbiddenError` (403)
  - `NotFoundError` (404)
  - `ValidationError` (400)
  - `AIUnavailableError` (503 with graceful degradation)
  - `ConflictError` (409)

- [x] T021 [P] Create `backend/app/utils/logger.py` with structured logging configuration using Python logging module

### Base Models & Schemas

- [x] T022 Create `backend/app/models/__init__.py` to export all models (User, Task, TaskShare, etc.)
- [x] T023 [P] Create `backend/app/models/base.py` with:
  - `Base` class for SQLAlchemy with UUID primary keys
  - Timestamp mixins (created_at, updated_at)
  - Utility methods (as_dict, to_dict with relationships)

- [x] T024 Create `backend/app/models/user.py` with User SQLAlchemy model:
  - Fields: id (UUID PK), email (VARCHAR UNIQUE), password_hash, full_name, created_at, updated_at, is_active
  - Relationships: tasks (one-to-many), task_shares (one-to-many)
  - Methods: __repr__, verify_password()

- [x] T025 [P] Create `backend/app/models/task.py` with Task model:
  - Fields: id, owner_id (FK User), title, description, status (enum), priority (enum), deadline, estimated_duration, created_at, updated_at, completed_at
  - Relationships: owner (FK User), task_shares (one-to-many)
  - Enums: TaskStatus (pending, in_progress, completed), TaskPriority (low, medium, high, urgent)

- [x] T026 Create `backend/app/schemas/__init__.py` to export all Pydantic schemas
- [x] T027 [P] Create `backend/app/schemas/user.py` with Pydantic schemas:
  - `UserRegister` (email, password, full_name optional)
  - `UserResponse` (id, email, full_name, created_at)
  - `UserInDB` (extends UserResponse + password_hash for internal use)

- [x] T028 [P] Create `backend/app/schemas/task.py` with Pydantic schemas:
  - `TaskCreate` (title, description optional, deadline optional)
  - `TaskUpdate` (title, description, status, priority, deadline - all optional)
  - `TaskResponse` (all fields + relationships)
  - `TaskInDB` (internal schema)

- [x] T029 [P] Create `backend/app/schemas/shared.py` with common schemas:
  - `ErrorDetail` (code, message, details optional)
  - `ErrorResponse` (status="error", error: ErrorDetail)
  - `SuccessResponse` (status="success", data: object)
  - `PaginationParams` (skip, limit with defaults)

### API Framework & Middleware

- [x] T030 Create `backend/app/config.py` with:
  - `Settings` dataclass using environment variables
  - Database URL, OpenAI API key, JWT config, CORS allowed origins
  - Debug mode flag

- [x] T031 Create `backend/app/main.py` with FastAPI initialization:
  - FastAPI app instance with title, description, version
  - CORS middleware configured from ALLOWED_ORIGINS
  - Exception handlers for custom exceptions (InvalidCredentialsError → 401, ForbiddenError → 403, etc.)
  - GET `/health` endpoint returning {"status": "healthy"}
  - Router setup: `/api/v1/auth`, `/api/v1/tasks`, `/api/v1/ai` (no routes yet, just structure)

- [x] T032 [P] Create `backend/app/api/__init__.py` to export routers

### Frontend Framework & Layout

- [x] T033 Create `frontend/src/app/layout.tsx` (root layout) with:
  - React providers (auth context, UI theme)
  - Header and basic navigation
  - Children rendering

- [x] T034 Create `frontend/src/app/page.tsx` (home/login page) with conditional render:
  - If authenticated: redirect to /dashboard
  - If not: show login/register page selector

- [x] T035 [P] Create `frontend/src/types/index.ts` with TypeScript types:
  - `User` (id, email, full_name, created_at)
  - `Task` (id, title, description, status, priority, deadline, estimated_duration, created_at, updated_at, completed_at)
  - `AuthToken` (access_token, token_type, expires_in)
  - `API Response types` (success/error structure)

- [x] T036 [P] Create `frontend/src/services/api.ts` with:
  - axios instance configured with NEXT_PUBLIC_API_URL
  - Request interceptor to add Authorization header if token present
  - Response interceptor to handle 401 (redirect to login) and other errors
  - Base API call error handling

- [x] T037 [P] Create `frontend/src/store/authStore.ts` with Zustand store:
  - State: user, accessToken, isAuthenticated
  - Actions: setUser, setTokens, logout, clearAuth
  - Persistent storage of tokens in localStorage

- [x] T038 [P] Create `frontend/src/hooks/useAuth.ts` custom hook:
  - Returns user, isLoading, error from authStore
  - login(email, password) method
  - register(email, password, full_name) method
  - logout() method

### Error Handling & Response Format Validation

- [x] T039 Create `backend/app/utils/response.py` with:
  - `create_success_response(data, status_code=200)` helper
  - `create_error_response(code, message, details=None, status_code=400)` helper
  - Ensures all responses follow standard format (status + data/error)

- [x] T040 [P] Create middleware in `backend/app/main.py` to:
  - Catch all unhandled exceptions
  - Log exceptions
  - Return standardized error response with 500 status for unexpected errors

### Testing Infrastructure (Optional but Recommended)

- [x] T041 Create `backend/tests/conftest.py` with pytest fixtures:
  - `test_db` fixture for test database session
  - `client` fixture for test API client (TestClient from fastapi.testclient)
  - `test_user` fixture creating a test user in test_db
  - `test_task` fixture creating a test task for test_user

- [x] T042 [P] Create `backend/tests/__init__.py` and test directories: unit/, integration/

**Checkpoint**: Foundational infrastructure complete. Database, auth, models, API framework, frontend framework, and error handling all set up. Ready to begin user story implementation.

---

## Phase 3: User Story 1 - Create and Manage Tasks with AI Assistance (Priority: P1) 🎯 MVP

**Goal**: Enable authenticated users to create tasks with AI-generated priority recommendations, view tasks organized by status, update and delete tasks. Core functionality with AI enhancement.

**Independent Test**: User can register → login → create task with natural language → see AI suggestions (priority, duration) → view task in dashboard → update status → delete task. All data persists in PostgreSQL.

**Acceptance Criteria**:
1. User creates task "Review quarterly reports and prepare summary by Friday"
2. System generates priority (high/urgent) and estimates duration (3 hours)
3. User views dashboard with task organized by status
4. User updates task status to "in_progress"
5. User can complete and delete task
6. Task data persists across page refreshes

### Backend Implementation for US1

#### User Registration & Authentication

- [x] T043 Create `backend/app/api/auth.py` router with:
  - POST `/register` endpoint (UserRegister → UserResponse, 201)
    - Validate email format and password strength (min 12 chars)
    - Hash password using auth_service
    - Create user in database
    - Handle duplicate email error (409 Conflict)
  - POST `/login` endpoint (email, password → AuthToken, 200)
    - Find user by email
    - Verify password
    - Create access + refresh tokens
    - Return AuthToken with expiration
    - Handle invalid credentials (401)

- [x] T044 [P] Create `backend/app/services/user_service.py` with:
  - `create_user(db, email, password, full_name)` → User object
  - `get_user_by_email(db, email)` → User or None
  - `get_user_by_id(db, user_id)` → User or None

#### Task CRUD Operations

- [x] T045 Create `backend/app/api/tasks.py` router with:
  - GET `/` (list tasks for authenticated user)
    - Query params: status (filter), priority (filter), skip (default 0), limit (default 20)
    - Return paginated list: {items: [Task], total: int, skip: int, limit: int}
    - Uses get_current_user dependency
  - POST `/` (create new task)
    - Request: TaskCreate (title, description, deadline)
    - Call task_service.create_task()
    - Call ai_service.generate_priority_and_duration() async (non-blocking)
    - Return TaskResponse with AI suggestions (201)
  - GET `/{task_id}` (get single task)
    - Verify user has access (owns task or shared)
    - Return TaskResponse
  - PUT `/{task_id}` (update task)
    - Request: TaskUpdate (partial fields)
    - Verify ownership
    - Call task_service.update_task()
    - Return updated TaskResponse
  - DELETE `/{task_id}` (delete task)
    - Verify ownership
    - Call task_service.delete_task()
    - Return 204 No Content

- [x] T046 Create `backend/app/services/task_service.py` with:
  - `create_task(db, user_id, title, description, deadline)` → Task
  - `get_task(db, task_id, user_id)` → Task or raise NotFoundError
  - `get_user_tasks(db, user_id, status=None, priority=None, skip=0, limit=20)` → (tasks, total_count)
  - `update_task(db, task_id, user_id, **kwargs)` → Task
  - `delete_task(db, task_id, user_id)` → None
  - `can_access_task(db, task_id, user_id)` → bool (checks ownership or shares)

#### AI Service Integration (OpenAI Agents SDK)

- [x] T047 Create `backend/app/services/ai_service.py` with OpenAI Agents SDK integration:
  - `generate_priority_and_duration(task_description)` → (priority_str, estimated_hours)
    - Uses OpenAI Agents SDK to analyze task description
    - Returns enum-compatible priority ("low"/"medium"/"high"/"urgent")
    - Returns integer hours estimate (1-999)
    - Handles OpenAI API failures gracefully: returns (None, None) without raising
    - Includes timeout (3 seconds) and rate limiting via decorator
    - Logs all AI API calls to audit_log table
  - `suggest_subtasks(task_id, task_description)` → List[str] (for P2)
    - Deferred to P2; stub for now
  - Async support: methods are async-compatible for non-blocking execution

- [x] T048 [P] Create `backend/app/utils/decorators.py` with:
  - `@rate_limit(max_calls=10, time_window=60)` decorator for OpenAI API calls
  - `@timeout(seconds=3)` decorator for AI feature latency constraint

#### Task Models Update

- [x] T049 Update `backend/app/models/task.py` to add:
  - `ai_priority` field (nullable) - stores AI-generated priority
  - `ai_estimated_duration` field (nullable) - stores AI-generated hours estimate
  - Method: `update_ai_suggestions(priority, duration)` to set these fields

### Frontend Implementation for US1

#### Authentication UI

- [x] T050 Create `frontend/src/app/auth/login/page.tsx` with:
  - Email and password form inputs
  - "Login" button
  - "Don't have account? Register" link
  - Error message display for invalid credentials
  - Loading state during login
  - Redirect to /dashboard on success
  - Uses useAuth hook for login method

- [x] T051 [P] Create `frontend/src/app/auth/register/page.tsx` with:
  - Email, password, confirm password, full_name form inputs
  - Password strength validation (min 12 chars)
  - "Register" button
  - "Already have account? Login" link
  - Error display
  - Loading state
  - Redirect to login on success
  - Uses useAuth hook for register method

- [x] T052 [P] Create `frontend/src/components/auth/LoginForm.tsx` component (reusable form)
  - Email input field
  - Password input field
  - Submit button with loading state
  - Error message display
  - Calls onSubmit prop with (email, password)

#### Dashboard & Task List

- [x] T053 Create `frontend/src/app/dashboard/page.tsx` main dashboard with:
  - Protected route (redirect to login if not authenticated)
  - Task list component
  - Create task button
  - Status filter tabs (All, Pending, In Progress, Completed)
  - Uses useTasks hook for task data

- [x] T054 Create `frontend/src/app/dashboard/layout.tsx` with:
  - Header with user name, logout button
  - Sidebar with navigation
  - Protected route wrapper

- [x] T055 Create `frontend/src/app/dashboard/components/TaskList.tsx` with:
  - Display tasks as list or grid
  - Show each task: title, priority badge, status, deadline
  - onClick to open task detail modal
  - Loading skeleton while fetching
  - Empty state message

- [x] T056 [P] Create `frontend/src/app/dashboard/components/TaskItem.tsx` task card component:
  - Title, priority (color-coded: low=gray, medium=yellow, high=orange, urgent=red)
  - Status dropdown (pending, in_progress, completed)
  - Deadline if present
  - AI suggestions indicator (if available)
  - Delete button

- [x] T057 [P] Create `frontend/src/app/dashboard/components/TaskForm.tsx` create/edit form:
  - Title input (required)
  - Description textarea (optional)
  - Deadline date picker (optional)
  - "Create" or "Update" button based on isEdit prop
  - Cancel button
  - Calls onSubmit prop with form data

#### State Management & Hooks

- [x] T058 Create `frontend/src/store/taskStore.ts` Zustand store with:
  - State: tasks: Task[], filters: {status?, priority?}, isLoading, error
  - Actions: setTasks, addTask, updateTask, deleteTask, setFilters
  - Computed: filteredTasks (applying status/priority filters)

- [x] T059 Create `frontend/src/hooks/useTasks.ts` custom hook:
  - fetchTasks(filters) - GET /api/v1/tasks with filters
  - createTask(title, description, deadline) - POST /api/v1/tasks
  - updateTask(task_id, updates) - PUT /api/v1/tasks/{task_id}
  - deleteTask(task_id) - DELETE /api/v1/tasks/{task_id}
  - Returns: {tasks, isLoading, error, fetchTasks, createTask, updateTask, deleteTask}

- [x] T060 [P] Create `frontend/src/hooks/useApi.ts` generic API hook:
  - useFetch(url) - generic GET hook with loading/error states
  - usePost(url) - generic POST hook
  - usePut(url) - generic PUT hook
  - useDelete(url) - generic DELETE hook

#### AI Suggestions Display

- [x] T061 Create `frontend/src/app/dashboard/components/AIInsights.tsx` component:
  - Display priority badge with AI label ("AI: High")
  - Display estimated duration ("Est: 3 hours")
  - Show loading spinner while AI generating
  - Show error message if AI unavailable
  - Graceful degradation: still shows task without AI data

#### API Integration

- [x] T062 Create `frontend/src/services/tasks.ts` API client functions:
  - `getTasks(filters)` → calls GET /api/v1/tasks
  - `getTask(task_id)` → calls GET /api/v1/tasks/{task_id}
  - `createTask(data)` → calls POST /api/v1/tasks
  - `updateTask(task_id, data)` → calls PUT /api/v1/tasks/{task_id}
  - `deleteTask(task_id)` → calls DELETE /api/v1/tasks/{task_id}

### Testing for US1 (Optional but Recommended for MVP)

- [x] T063 Create `backend/tests/integration/test_auth_api.py` with tests:
  - Test user registration with valid data → 201 + UserResponse
  - Test login with correct credentials → 200 + AuthToken
  - Test login with incorrect password → 401
  - Test register with duplicate email → 409
  - Test register with weak password → 400

- [x] T064 Create `backend/tests/integration/test_task_api.py` with tests:
  - Test create task (authenticated) → 201 + TaskResponse with AI suggestions
  - Test get task list (authenticated, no filters) → 200 + paginated list
  - Test get task list with status filter → only returns matching tasks
  - Test update task status → 200 + updated task
  - Test delete task → 204
  - Test create task without auth → 401

- [x] T065 [P] Create `frontend/src/__tests__/auth.test.tsx` with tests:
  - Test login form renders with email/password fields
  - Test login button disabled while loading
  - Test error message displays on 401
  - Test successful login redirects to dashboard

- [x] T066 [P] Create `frontend/src/__tests__/tasks.test.tsx` with tests:
  - Test task list renders tasks
  - Test create task form submission calls API
  - Test AI priority badge displays
  - Test filter by status works

**Checkpoint**: User Story 1 (MVP) is complete and independently testable. Users can register, login, create tasks with AI suggestions, view dashboard, update/delete tasks. Core functionality working with PostgreSQL persistence.

---

## Phase 4: User Story 2 - AI-Powered Task Analysis and Recommendations (Priority: P2)

**Goal**: Enable users to ask natural language questions about tasks and receive AI-powered insights. Analyze task dependencies, scheduling recommendations, and historical patterns.

**Independent Test**: User selects task → asks "What are the dependencies?" → receives AI analysis about what needs to happen first → updates task based on recommendations. AI features work independently of P1.

**Acceptance Criteria**:
1. User asks AI "What dependencies exist?" on "Build REST API" task
2. AI responds with: "Consider database schema, testing framework, documentation"
3. User can ask follow-up questions
4. AI handles rate limiting gracefully

### Backend Implementation for US2

- [ ] T067 Update `backend/app/models/task.py` to add:
  - `dependencies` field (JSON array, optional) - tracks task dependencies
  - `related_tasks` field (relationship to other tasks, optional)

- [ ] T068 Create `backend/app/api/ai.py` router with:
  - POST `/tasks/{task_id}/analyze` endpoint (question → {answer, suggestions, confidence})
    - Request: {question: str}
    - Call ai_service.analyze_task_query(task_id, task_data, question)
    - Return AI response with suggestions array
    - Handle AI unavailability (503) without blocking

- [ ] T069 Update `backend/app/services/ai_service.py` to add:
  - `analyze_task_query(task_id, task_description, question)` → (answer_str, suggestions_list, confidence_score)
    - Uses OpenAI Agents SDK for task context analysis
    - Retrieves task history and similar completed tasks
    - Generates dependency analysis
    - Includes timeout (3 sec) and logging
  - `suggest_subtasks(task_id, task_description)` → List[str]
    - Uses AI to break down complex task into subtasks
    - Returns 2-5 suggested subtasks

- [ ] T070 [P] Update `backend/app/services/task_service.py` to add:
  - `get_similar_tasks(db, task_id, user_id, limit=5)` → List[Task]
    - Finds recently completed tasks with similar keywords
  - `extract_dependencies(task_id, task_data, ai_response)` → List[str]
    - Parses AI analysis to extract dependency suggestions
    - Stores in task.dependencies field

- [ ] T071 Update `backend/app/models/audit_log.py` (or create if doesn't exist):
  - Track all AI API calls: timestamp, user_id, task_id, api_endpoint, token_count, latency, success/failure
  - Used for monitoring, billing, and debugging

### Frontend Implementation for US2

- [ ] T072 Create `frontend/src/app/dashboard/components/TaskDetail.tsx` modal/page with:
  - Task information display (title, description, status, deadline, AI suggestions from P1)
  - "Ask AI" input field and button
  - AI response area with answer and suggestions
  - Loading state while AI thinking
  - Error message if AI unavailable ("AI features temporarily unavailable")
  - Suggestion chips user can click to apply

- [ ] T073 Create `frontend/src/app/dashboard/components/AIChat.tsx` component:
  - Input field for natural language questions
  - Send button (enabled after typing)
  - Message history (Q&A format)
  - Thinking indicator while awaiting response
  - Suggestion pills that auto-populate input

- [ ] T074 [P] Update `frontend/src/store/taskStore.ts` to add:
  - aiResponse: {question, answer, suggestions, confidence} state
  - setAiResponse action
  - clearAiResponse action

- [ ] T075 [P] Create `frontend/src/hooks/useAi.ts` custom hook:
  - analyzeTask(task_id, question) → {answer, suggestions, confidence}
  - Handles AI unavailable error (shows toast, graceful degradation)
  - Sets loading state during API call

- [ ] T076 Create `frontend/src/services/ai.ts` API client:
  - `analyzeTask(task_id, question)` → POST /api/v1/tasks/{task_id}/ai/analyze
  - Returns response with answer, suggestions, confidence score

### Testing for US2

- [ ] T077 Create `backend/tests/integration/test_ai_api.py` with tests:
  - Test analyze task with valid question → 200 + response with answer/suggestions
  - Test AI unavailable → 503 with graceful degradation message
  - Test rate limiting → returns 429 after exceeding limit
  - Test task not found → 404

- [ ] T078 [P] Create `frontend/src/__tests__/ai.test.tsx` with tests:
  - Test AI chat input and send button
  - Test AI response displays in chat
  - Test error message on AI unavailable
  - Test suggestion chips clickable

**Checkpoint**: User Story 2 complete. Users can ask AI questions about tasks, receive analysis, view suggestions. Works independently of P1.

---

## Phase 5: User Story 3 - Real-Time Collaboration and Team Features (Priority: P3)

**Goal**: Enable users to share tasks with team members, assign tasks, and see real-time updates. Comments and file collaboration (deferred).

**Independent Test**: User A creates task → shares with User B → User B sees task in "Assigned to Me" → User B updates status → User A sees change (within 5 seconds via polling). No P1/P2 blocking.

**Acceptance Criteria**:
1. User A shares task with User B (editor role)
2. User B receives notification and can access task
3. User B updates task status
4. User A sees status change (within 5 sec polling interval)
5. User A can unshare/revoke access

### Backend Implementation for US3

#### Task Sharing & Access Control

- [ ] T079 Create `backend/app/models/task_share.py` model with:
  - Fields: id (UUID), task_id (FK Task), user_id (FK User), role (enum: owner/editor/viewer), shared_at, created_by (FK User)
  - Relationships: task, user, created_by_user
  - Indexes: (task_id, user_id) composite unique

- [ ] T080 Create `backend/app/schemas/share.py` Pydantic schemas:
  - `TaskShareCreate` (user_email, role: editor|viewer)
  - `TaskShareResponse` (user_id, role, shared_at)
  - `TaskShareUpdate` (role: editor|viewer)

- [ ] T081 Update `backend/app/api/tasks.py` to add routes:
  - GET `/tasks/{task_id}/shares` - list all shares for task (only owner)
  - POST `/tasks/{task_id}/share` - share task with user
    - Request: {user_email, role}
    - Finds user by email, creates TaskShare
    - Returns 201 TaskShareResponse
  - DELETE `/tasks/{task_id}/shares/{share_id}` - revoke share (only owner)
    - Returns 204

- [ ] T082 Create `backend/app/api/shared_tasks.py` router:
  - GET `/me/shared-with-me` - tasks shared with current user
    - Returns paginated list of shared tasks
  - GET `/me/shared-by-me` - tasks current user has shared
    - Returns paginated list

- [ ] T083 Update `backend/app/services/task_service.py` to add:
  - `share_task(db, task_id, owner_id, user_email, role)` → TaskShare
    - Finds user by email, creates share relationship
    - Validates owner is task owner
  - `revoke_share(db, share_id, owner_id)` → None
    - Deletes share relationship
  - `get_user_accessible_tasks(db, user_id, skip=0, limit=20)` → (tasks, count)
    - Returns owned + shared tasks with role info
  - Update `can_access_task()` to check TaskShare table

- [ ] T084 [P] Update `backend/app/services/task_service.py`:
  - `update_task_shared_with_user()` - updates shared task if user has editor role
  - Permission check: user_id must have editor+ role in TaskShare

#### Real-Time Updates (Polling MVP)

- [ ] T085 Create `backend/app/api/tasks.py` new endpoint:
  - GET `/tasks?modified_since={timestamp}` - returns tasks modified after timestamp
    - Uses `task.updated_at` field for change detection
    - Frontend can poll every 3-5 seconds
    - Reduces payload vs fetching all tasks

- [ ] T086 Update task models to add:
  - `last_modified_by` field (FK User) - tracks who last modified task
  - Used for audit/notification purposes

#### Notifications (Email deferred, in-app only for MVP)

- [ ] T087 Create `backend/app/models/notification.py` model:
  - Fields: id, user_id (FK), event_type (task_shared, task_updated), task_id, message, read_at, created_at
  - Used for notification center (UI shows 1-2 notifications)

- [ ] T088 Create notification service stub in `backend/app/services/notification_service.py`:
  - `create_notification(db, user_id, event_type, task_id, message)`
  - Defers email sending to future phase; just stores notification

### Frontend Implementation for US3

#### Task Sharing UI

- [ ] T089 Update `frontend/src/app/dashboard/components/TaskDetail.tsx` to add:
  - "Share" button opens share modal
  - Share modal with email input + role dropdown (editor/viewer)
  - List of current shares with revoke button (only for owner)

- [ ] T090 Create `frontend/src/app/dashboard/components/ShareTaskModal.tsx` component:
  - Email input field
  - Role selector (editor, viewer)
  - "Share" button
  - Shared users list with delete button
  - Error handling (user not found, already shared)
  - Calls shareTask API

- [ ] T091 Create `frontend/src/app/dashboard/components/AssignedToMe.tsx` view:
  - Tab in dashboard: "Assigned to Me"
  - Lists tasks shared with current user
  - Shows role (editor/viewer) as badge
  - Can update status if editor role
  - Can only view if viewer role

#### Real-Time Update Integration

- [ ] T092 Update `frontend/src/hooks/useTasks.ts` to add:
  - `startPolling(interval_ms = 3000)` - polls /tasks?modified_since=lastSync
  - `stopPolling()` - cancels polling
  - Auto-refresh dashboard every 3-5 seconds for shared tasks
  - Preserves local changes while polling (optimistic updates)

- [ ] T093 Update `frontend/src/app/dashboard/page.tsx` to:
  - Call startPolling on mount
  - Call stopPolling on unmount
  - Show "Real-time updates enabled" indicator
  - Highlight recently updated tasks (last 5 seconds)

#### API Integration

- [ ] T094 Update `frontend/src/services/tasks.ts`:
  - `shareTask(task_id, user_email, role)` → POST /api/v1/tasks/{task_id}/share
  - `revokeShare(task_id, share_id)` → DELETE /api/v1/tasks/{task_id}/shares/{share_id}
  - `getSharedWithMe()` → GET /api/v1/me/shared-with-me
  - `getTasksSince(timestamp)` → GET /api/v1/tasks?modified_since=timestamp

- [ ] T095 [P] Update `frontend/src/store/taskStore.ts`:
  - `lastSyncTimestamp` state for polling
  - `updateLastSync()` action
  - `sharedUsers` state for current task shares

- [ ] T096 [P] Create `frontend/src/hooks/useSharing.ts`:
  - `shareTask(task_id, email, role)`
  - `revokeShare(task_id, share_id)`
  - `getSharedTasks()`
  - Returns {sharedTasks, isLoading, error, shareTask, revokeShare}

### Testing for US3

- [ ] T097 Create `backend/tests/integration/test_sharing_api.py`:
  - Test share task with valid user → 201 TaskShareResponse
  - Test share task with non-existent user → 404
  - Test revoke share → 204
  - Test access control (non-owner can't share) → 403
  - Test editor can update, viewer can't → 403
  - Test get shared tasks → returns correct list

- [ ] T098 [P] Create `frontend/src/__tests__/sharing.test.tsx`:
  - Test share modal renders email input
  - Test share button disabled until email entered
  - Test shared tasks appear in "Assigned to Me"
  - Test real-time polling updates task

**Checkpoint**: User Story 3 complete. Task sharing, access control, and real-time polling working. All three user stories independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements, testing, documentation, and performance optimization affecting multiple user stories

- [ ] T099 [P] Add unit tests in `backend/tests/unit/test_models.py`:
  - Test all SQLAlchemy model creation and validation
  - Test model methods and relationships

- [ ] T100 [P] Add unit tests in `backend/tests/unit/test_services.py`:
  - Test service methods with mocked DB
  - Test error handling paths

- [ ] T101 Run full test suite and achieve 70%+ code coverage:
  - `pytest --cov=app tests/`
  - Fix coverage gaps

- [ ] T102 [P] Add frontend TypeScript strict checks:
  - `npm run type-check` should pass with no errors
  - Add missing type definitions

- [ ] T103 [P] Add OpenAI Agents SDK context7 documentation integration:
  - Create `backend/app/docs/ai_integration.md` explaining:
    - How to use OpenAI Agents SDK for task analysis
    - Prompt engineering guidelines for task descriptions
    - Error handling for API failures
    - Rate limiting and cost considerations
  - Link to context7 MCP server for live documentation

- [ ] T104 Update `backend/README.md` with:
  - Setup instructions using quickstart.md
  - API documentation links
  - Architecture overview
  - Contributing guidelines

- [ ] T105 [P] Update `frontend/README.md` with:
  - Setup instructions
  - Component structure
  - State management guide
  - Testing instructions

- [ ] T106 Create `docs/DEPLOYMENT.md` with:
  - Docker build instructions
  - Environment configuration for production
  - Database migration procedures
  - Monitoring and alerting setup

- [ ] T107 [P] Performance optimization:
  - Backend: Add database query indexing verification
  - Frontend: Implement code splitting for dashboard routes
  - Frontend: Lazy load AI features
  - Frontend: Optimize images/assets

- [ ] T108 [P] Security hardening:
  - Backend: Add rate limiting per IP/user
  - Backend: Add CSRF protection if applicable
  - Frontend: Enable strict CSP headers
  - Verify all inputs validated and sanitized

- [ ] T109 Validate against success criteria:
  - SC-001: Task creation < 5 seconds (measure end-to-end)
  - SC-002: Data persistence (verify 100% of creates persisted)
  - SC-003: AI suggestions generated for 95% of tasks
  - SC-004: Error handling for API failures
  - SC-005: Load test with 100+ tasks
  - SC-006: AI response latency < 3 seconds
  - SC-007: Task CRUD works when OpenAI unavailable
  - SC-008: Shared tasks visible within 2 seconds
  - SC-009: Dashboard loads < 2 seconds with 500 tasks

- [ ] T110 Run quickstart.md validation:
  - Follow setup steps exactly
  - Verify all endpoints work
  - Verify frontend login/create task flow
  - Document any issues found

- [ ] T111 [P] Setup CI/CD pipeline (.github/workflows/ or similar):
  - Lint checks (flake8, black, eslint)
  - Type checks (mypy, typescript)
  - Test execution (pytest, jest)
  - Build verification

**Checkpoint**: Application is production-ready. All user stories tested, documented, optimized. Ready for deployment.

---

## Dependencies & Execution Order

### Phase Dependencies (CRITICAL)

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
    ├→ Phase 3 (US1 - MVP)
    │     ├→ Phase 4 (US2 - P2)
    │     │     └→ Phase 5 (US3 - P3)
    │
    └→ Phase 6 (Polish) ← After desired user stories done
```

**CRITICAL**: Phase 2 MUST complete before any user story work begins. Phase 1 has no dependencies.

### Within Phase Execution

- **Phase 1 Setup**: Tasks T001-T014
  - All [P] tasks can run in parallel
  - Non-parallel tasks in sequence shown

- **Phase 2 Foundational**: Tasks T015-T042
  - Database setup (T015-T017) first
  - Auth/models (T018-T032) can run parallel after DB
  - Frontend framework (T033-T038) parallel to backend
  - Testing setup (T041-T042) parallel
  - **Checkpoint must be reached before Phase 3**

- **Phase 3 US1**: Tasks T043-T066
  - Auth endpoints (T043-T044) before other endpoints
  - Models (T045-T049) parallel to services
  - Services (T046-T048) before endpoints
  - Frontend components (T050-T062) all parallel
  - Testing can start once implementation tasks done

- **Phase 4 US2**: Tasks T067-T078
  - Can start after Phase 2 complete (doesn't require Phase 3)
  - Backend (T067-T078) and frontend (T072-T078) parallel
  - But will integrate with P1 components in production

- **Phase 5 US3**: Tasks T079-T098
  - Can start after Phase 2 complete
  - Can run parallel with P2 if team has capacity
  - Sharing model (T079-T084) before sharing endpoints
  - Frontend (T089-T098) parallel to backend

- **Phase 6 Polish**: Tasks T099-T111
  - Can start once desired user stories done
  - All [P] tasks run parallel
  - Final validation/testing

### Recommended Execution Strategy

**For single developer**:
1. Complete Phase 1 (Setup) - 1-2 hours
2. Complete Phase 2 (Foundational) - 3-4 hours
3. Complete Phase 3 (US1 MVP) - 6-8 hours
4. Complete Phase 4 (US2) - 4-6 hours
5. Complete Phase 5 (US3) - 4-6 hours
6. Complete Phase 6 (Polish) - 2-3 hours
**Total**: ~20-30 hours for complete MVP

**For team of 2-3**:
1. Phase 1: 1 person (1-2 hours)
2. Phase 2: 1-2 people (3-4 hours)
3. Phase 3 + Phase 4: 2 people in parallel (10-14 hours, do P1 first then P2 after)
4. Phase 5: 1 person while others polish (4-6 hours)
5. Phase 6: All together (2-3 hours)
**Total**: ~10-15 hours parallel time

---

## Parallel Opportunities

### Phase 1 (Setup) Parallel

```bash
# Team Person A: Backend setup
T001 Create backend dir structure
T002 Create pyproject.toml
T003 Create requirements.txt
→ T015-T017 Database setup

# Team Person B: Frontend setup
T006 Create frontend package.json
T007 Create .env.example
T008-T011 Frontend config files
→ T033-T038 Frontend framework

# Team Person C: Docker
T013 Create docker-compose.yml
T014 Create root .env.example
```

### Phase 2 (Foundational) Parallel

```bash
# Team A: Backend models & auth
T015 Alembic init
T016 Database session
T017 Initial migration
T018-T021 Auth service & exceptions
T022-T025 Models (User, Task, TaskShare)

# Team B: Backend schemas & API framework
T026-T029 Pydantic schemas
T030-T032 API framework (main.py, routers)

# Team C: Frontend framework
T033-T038 Layout, pages, types, services, stores, hooks
T039-T040 Response format & error handling

# Team D: Testing
T041-T042 Test fixtures & directories
```

### Phase 3 (US1) Parallel

```bash
# Team A: Backend US1
T043-T044 Auth endpoints
T045-T046 Task endpoints & service
T047-T048 AI service
T049 Task model update

# Team B: Frontend US1 (can start after T033-T038)
T050-T061 Auth UI, Dashboard, Task components, API integration
T062 Task API service

# Team C: Testing (can start after implementation)
T063-T066 Integration and component tests
```

### Phase 4 (US2) Parallel with Phase 3

```bash
# If team has capacity during Phase 3 final days:
# Team D: US2 Backend (T067-T071)
# Team E: US2 Frontend (T072-T076)
# These don't block P1, can develop independently
```

---

## MVP Scope & Incremental Delivery

**MVP Minimum**: Phase 1 + Phase 2 + Phase 3 US1
- User registration & login
- Task CRUD
- AI priority/duration suggestions
- Task persistence in PostgreSQL
- Basic dashboard

**MVP+1**: Add Phase 4 US2
- AI task analysis
- Natural language questions
- Suggestions/recommendations

**MVP+2**: Add Phase 5 US3
- Task sharing
- Team collaboration
- Real-time updates via polling

**Full Release**: Phase 6 Polish
- Comprehensive testing
- Optimization
- Documentation
- Deployment readiness

---

## OpenAI Agents SDK & Context7 Integration

**Backend AI Layer** (US1, US2):
- Located in: `backend/app/services/ai_service.py`
- Uses: OpenAI Agents SDK for task analysis, priority generation, dependency extraction
- Context7 MCP Server: Reference documentation at runtime for:
  - Agent prompt engineering best practices
  - Token usage optimization
  - Model selection (gpt-4o-mini recommended for MVP cost)
  - Error handling patterns
  - Rate limiting strategies
- Documentation: `backend/app/docs/ai_integration.md` links to context7 live docs

**Key Integration Points**:
- `generate_priority_and_duration()` - Uses agent for task complexity analysis
- `analyze_task_query()` - Uses agent for natural language Q&A
- `suggest_subtasks()` - Uses agent for task decomposition

**Graceful Degradation**:
- Task CRUD works 100% without AI
- AI features return sensible defaults (no priority, no suggestions) if unavailable
- User sees "AI features temporarily unavailable" message (not error)

---

## Summary

**Total Tasks**: 111 across 6 phases
**User Stories**: 3 (P1, P2, P3)
**Files to Create**: ~80+ (backend + frontend + tests)
**Estimated Effort**: 20-30 hours (single dev), 10-15 hours parallel (team of 3)

**Phase Breakdown**:
- Phase 1 (Setup): 14 tasks
- Phase 2 (Foundational): 28 tasks ← CRITICAL BLOCKER
- Phase 3 (US1 MVP): 24 tasks
- Phase 4 (US2 P2): 12 tasks
- Phase 5 (US3 P3): 20 tasks
- Phase 6 (Polish): 13 tasks

**Ready to Begin**: Yes - All prerequisites met, all paths defined, all dependencies clear.

---

**Related Documents**:
- Specification: `specs/002-fullstack-ai-todo/spec.md`
- Architecture Plan: `specs/002-fullstack-ai-todo/plan.md`
- Data Model: `specs/002-fullstack-ai-todo/data-model.md`
- API Contracts: `specs/002-fullstack-ai-todo/contracts/openapi.yaml`
- Developer Setup: `specs/002-fullstack-ai-todo/quickstart.md`
- Research & Decisions: `specs/002-fullstack-ai-todo/research.md`
