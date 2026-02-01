# Phase 1: Data Model & Schema Design

**Date**: 2025-12-08 | **Feature**: 002-fullstack-ai-todo | **Status**: Complete

## Database Entities

### 1. User (Core Entity)

Represents an authenticated application user.

**SQLAlchemy Model**: `app/models/user.py`

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email address (login credential) |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| full_name | VARCHAR(255) | NULLABLE | User's display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last profile update |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete flag |

**Indexes**:
- `idx_user_email`: UNIQUE index on email (fast login lookup)

**Relationships**:
- One User → Many Tasks (as owner)
- One User → Many TaskShares (as collaborator)

**Validation Rules**:
- Email: Valid RFC 5322 format, lowercase for normalization
- Password: Minimum 12 characters, bcrypt cost 12
- full_name: Optional, max 255 chars

**Use Cases**:
- User registration and authentication
- Task ownership tracking
- Collaboration (sharing tasks with other users)

---

### 2. Task (Core Entity - P1)

Represents a todo item with AI-generated metadata.

**SQLAlchemy Model**: `app/models/task.py`

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique task identifier |
| owner_id | UUID | FOREIGN KEY (users), NOT NULL | Task owner (creator) |
| title | VARCHAR(255) | NOT NULL | Task summary |
| description | TEXT | NULLABLE | Detailed task description |
| status | ENUM | NOT NULL, DEFAULT 'pending' | pending, in_progress, completed |
| priority | ENUM | NULLABLE | low, medium, high, urgent (AI-generated) |
| deadline | TIMESTAMP | NULLABLE | Optional due date |
| estimated_duration | INTEGER | NULLABLE | Estimated hours (AI-generated) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last modification |
| completed_at | TIMESTAMP | NULLABLE | When task was marked complete |

**Indexes**:
- `idx_task_owner_id`: Foreign key index for fast owner lookup
- `idx_task_status`: B-tree index on status for dashboard queries
- `idx_task_created_at`: For chronological listing
- `idx_task_owner_status`: Composite index on (owner_id, status) for filtered views

**Relationships**:
- Many Tasks → One User (owner)
- One Task → Many TaskShares (for collaboration)
- One Task → Many TaskComments (P3)

**Validation Rules**:
- title: Required, 1-255 characters
- description: Optional, max 10k characters
- status: One of (pending, in_progress, completed)
- priority: One of (low, medium, high, urgent) or NULL
- estimated_duration: If present, positive integer (hours)
- deadline: Must be in future; ISO 8601 format

**State Transitions**:
- pending → in_progress → completed (forward only, allows cycling back in MVP)
- Completed tasks retain completed_at timestamp for historical tracking

**Use Cases**:
- Create, read, update, delete tasks
- View tasks filtered by status or priority (dashboard)
- Historical analysis (when tasks were created, completed)
- AI feature: Generate priority and duration estimates

---

### 3. TaskShare (Collaboration Entity - P3)

Represents permission to access/edit a task by non-owner user.

**SQLAlchemy Model**: `app/models/task_share.py`

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Share relationship identifier |
| task_id | UUID | FOREIGN KEY (tasks), NOT NULL | Shared task |
| user_id | UUID | FOREIGN KEY (users), NOT NULL | User who can access |
| role | ENUM | NOT NULL | owner, editor, viewer (permission level) |
| shared_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When sharing occurred |
| created_by | UUID | FOREIGN KEY (users), NOT NULL | User who created the share |

**Indexes**:
- `idx_task_share_task_id`: For finding all shares of a task
- `idx_task_share_user_id`: For finding all tasks shared with a user
- `idx_task_share_unique`: UNIQUE constraint on (task_id, user_id) to prevent duplicate shares

**Relationships**:
- Many TaskShares → One Task
- Many TaskShares → One User (as collaborator)
- Many TaskShares → One User (as created_by)

**Validation Rules**:
- role: One of (owner, editor, viewer)
- user_id ≠ task.owner_id (don't need share entry for owner)
- Task owner can always modify; editor can change task details; viewer read-only

**Role Permissions**:
| Role | Can Read | Can Edit | Can Share | Can Delete |
|------|----------|----------|-----------|-----------|
| owner | ✅ | ✅ | ✅ | ✅ |
| editor | ✅ | ✅ | ❌ | ❌ |
| viewer | ✅ | ❌ | ❌ | ❌ |

**Use Cases**:
- Share task with team member (P3)
- Control who can edit vs. view
- Track who shared the task and when

---

### 4. TaskComment (Collaboration Entity - P3, Optional)

Represents conversation on a shared task.

**SQLAlchemy Model**: `app/models/task_comment.py`

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Comment identifier |
| task_id | UUID | FOREIGN KEY (tasks), NOT NULL | Parent task |
| author_id | UUID | FOREIGN KEY (users), NOT NULL | Comment author |
| content | TEXT | NOT NULL, MAX 5000 chars | Comment text |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Comment creation |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Edit timestamp |

**Indexes**:
- `idx_task_comment_task_id`: For retrieving all comments on a task
- `idx_task_comment_created_at`: For chronological ordering

**Relationships**:
- Many TaskComments → One Task
- Many TaskComments → One User (author)

**Validation Rules**:
- content: Required, 1-5000 characters
- author: User must have access to task (via TaskShare or ownership)

**Use Cases**:
- Team discussion on shared tasks (P3)
- Context and decisions recorded alongside task

---

### 5. AuditLog (Monitoring Entity - Optional)

Tracks important system events for monitoring, billing, and debugging.

**SQLAlchemy Model**: `app/models/audit_log.py`

| Field | Type | Constraints | Description |
|-------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Log entry identifier |
| user_id | UUID | FOREIGN KEY (users), NULLABLE | User who triggered event |
| event_type | VARCHAR(50) | NOT NULL | Event category (e.g., "task_created", "ai_call") |
| resource_type | VARCHAR(50) | NULLABLE | What was affected (task, user, etc.) |
| resource_id | UUID | NULLABLE | ID of affected resource |
| action | VARCHAR(50) | NOT NULL | Specific action (create, update, delete, call_ai) |
| status | ENUM | NOT NULL | success, failure |
| details | JSONB | NULLABLE | Event-specific metadata |
| error_message | TEXT | NULLABLE | If status=failure |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | When event occurred |

**Indexes**:
- `idx_audit_user_id`: For user activity tracking
- `idx_audit_created_at`: For time-range queries
- `idx_audit_event_type`: For filtering by event type

**Use Cases**:
- Monitor OpenAI API call volume and failures (billing)
- User activity audit trail (security)
- Debug customer issues ("what happened with task X?")
- Performance tracking (response times, error rates)

---

## Database Constraints & Integrity

### Foreign Key Constraints

```sql
-- Task.owner_id → User.id
ALTER TABLE tasks ADD CONSTRAINT fk_task_owner
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;

-- TaskShare.task_id → Task.id
ALTER TABLE task_shares ADD CONSTRAINT fk_share_task
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

-- TaskShare.user_id → User.id
ALTER TABLE task_shares ADD CONSTRAINT fk_share_user
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- TaskShare.created_by → User.id
ALTER TABLE task_shares ADD CONSTRAINT fk_share_created_by
  FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- TaskComment.task_id → Task.id
ALTER TABLE task_comments ADD CONSTRAINT fk_comment_task
  FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE;

-- TaskComment.author_id → User.id
ALTER TABLE task_comments ADD CONSTRAINT fk_comment_author
  FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL;

-- AuditLog.user_id → User.id
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_user
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;
```

### Unique Constraints

```sql
-- Email uniqueness
ALTER TABLE users ADD CONSTRAINT uk_user_email UNIQUE (email);

-- Prevent duplicate task shares
ALTER TABLE task_shares ADD CONSTRAINT uk_task_share_unique UNIQUE (task_id, user_id);
```

### Check Constraints

```sql
-- Valid task status
ALTER TABLE tasks ADD CONSTRAINT ck_task_status
  CHECK (status IN ('pending', 'in_progress', 'completed'));

-- Valid task priority
ALTER TABLE tasks ADD CONSTRAINT ck_task_priority
  CHECK (priority IS NULL OR priority IN ('low', 'medium', 'high', 'urgent'));

-- Valid share role
ALTER TABLE task_shares ADD CONSTRAINT ck_share_role
  CHECK (role IN ('owner', 'editor', 'viewer'));

-- Owner cannot share with themselves
ALTER TABLE task_shares ADD CONSTRAINT ck_share_not_owner
  CHECK (user_id != (SELECT owner_id FROM tasks WHERE id = task_id));

-- Audit log status
ALTER TABLE audit_logs ADD CONSTRAINT ck_audit_status
  CHECK (status IN ('success', 'failure'));
```

---

## ERD (Entity Relationship Diagram)

```
┌─────────────────────┐
│      Users          │
├─────────────────────┤
│ PK: id (UUID)       │
│ email (UNIQUE)      │
│ password_hash       │
│ full_name           │
│ created_at          │
└─────────────────────┘
        │
        │ 1:N
        ├─────────────────┐
        │                 │
        ▼                 ▼
┌──────────────────────┐  ┌──────────────────────┐
│      Tasks           │  │   TaskShares         │
├──────────────────────┤  ├──────────────────────┤
│ PK: id (UUID)        │  │ PK: id (UUID)        │
│ FK: owner_id         │  │ FK: task_id          │
│ title                │  │ FK: user_id          │
│ description          │  │ FK: created_by       │
│ status               │  │ role (enum)          │
│ priority (AI)        │  │ shared_at            │
│ deadline             │  └──────────────────────┘
│ estimated_duration   │
│ created_at           │
│ completed_at         │
└──────────────────────┘
        │
        │ 1:N (P3)
        │
        ▼
┌──────────────────────┐
│   TaskComments       │
├──────────────────────┤
│ PK: id (UUID)        │
│ FK: task_id          │
│ FK: author_id        │
│ content              │
│ created_at           │
└──────────────────────┘
```

---

## Migration Strategy

**Tool**: Alembic (SQLAlchemy migration framework)

**Migration Structure**:
```
backend/app/database/migrations/
├── alembic.ini
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py        # Users, Tasks tables
    ├── 002_task_share_schema.py     # TaskShare table (P3)
    ├── 003_add_task_comments.py     # TaskComment table (P3)
    └── 004_add_audit_logs.py        # AuditLog table (optional)
```

**First Migration** (001_initial_schema.py):
- Create users table with indexes
- Create tasks table with indexes and constraints
- Add foreign key from tasks → users
- Initialize with no data

**Deployment Process**:
```bash
# Local development
alembic upgrade head

# Production (CI/CD)
alembic upgrade head  # Automated before starting new backend version
```

**Rollback Support**:
```bash
# Revert last migration if needed
alembic downgrade -1
```

---

## Performance Considerations

### Query Patterns & Indexes

**Most Common Queries** (from spec requirements):

1. **Get user's tasks** (dashboard):
   ```sql
   SELECT * FROM tasks WHERE owner_id = ? AND status IN (?, ?, ?)
   ```
   **Index**: `idx_task_owner_status` (composite)

2. **Get shared tasks** (P3):
   ```sql
   SELECT t.* FROM tasks t
   JOIN task_shares ts ON t.id = ts.task_id
   WHERE ts.user_id = ? AND ts.role != 'viewer'
   ```
   **Index**: `idx_task_share_user_id`

3. **Get task by ID with permission check**:
   ```sql
   SELECT * FROM tasks WHERE id = ?
   ```
   **Index**: Primary key (automatic)

4. **Check if user can access task** (authorization):
   ```sql
   SELECT 1 FROM task_shares WHERE task_id = ? AND user_id = ? LIMIT 1
   ```
   **Index**: `idx_task_share_unique`

### Connection Pooling

**SQLAlchemy Pool Configuration**:
- Pool size: 10 connections (adjust per expected concurrent users)
- Max overflow: 20 (temporary burst connections)
- Pool recycle: 3600 seconds (1 hour, prevents stale connections)
- Echo: Disabled in production (SQL logging overhead)

### Caching Strategy (Optional, for P2)

Currently **N/A** for MVP. When added later:
- Cache user's task list (invalidate on create/update)
- Cache task detail by ID (invalidate on update)
- Cache user permissions (invalidate when share changes)

---

## Pydantic Schemas (Request/Response)

**Location**: `app/schemas/`

### User Schemas

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str  # minimum 12 chars, validated
    full_name: str | None = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None
    created_at: datetime

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
```

### Task Schemas

```python
class TaskCreate(BaseModel):
    title: str  # 1-255 chars
    description: str | None = None  # max 10k
    deadline: datetime | None = None
    # priority, estimated_duration generated by AI on create

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    deadline: datetime | None = None

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: str
    priority: str | None
    deadline: datetime | None
    estimated_duration: int | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True  # SQLAlchemy compatibility
```

### Error Schemas

```python
class ErrorDetail(BaseModel):
    code: str  # e.g., "VALIDATION_ERROR"
    message: str
    details: dict | None = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error: ErrorDetail
```

---

## Summary

Phase 1 data model is **complete and ready for implementation**. All entities, relationships, constraints, and validation rules are defined. Next steps:

1. Create API contracts (OpenAPI) in Phase 1
2. Create quickstart/developer setup guide
3. Proceed to Phase 2: Task breakdown (implementation tasks)

---

**Related Files**:
- Implementation Plan: `plan.md`
- Research & Decisions: `research.md`
- API Contracts: `contracts/openapi.yaml` (to be created)
- Database Migrations: `backend/app/database/migrations/`
