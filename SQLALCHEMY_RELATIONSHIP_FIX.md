# SQLAlchemy Relationship Fix

**Date**: December 9, 2025
**Error**: AmbiguousForeignKeysError in User.task_shares relationship
**Status**: ✅ FIXED

---

## Problem Explained

### The Error
```
sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join condition between parent/child
tables on relationship User.task_shares - there are multiple foreign key paths linking the tables.
Specify the 'foreign_keys' argument...
```

### Root Cause
The `TaskShare` model has **two foreign keys** that point to the `User` table:
1. `user_id` - The user receiving the shared task
2. `created_by` - The user who shared the task

SQLAlchemy couldn't determine which foreign key to use for the `User.task_shares` relationship because both foreign keys pointed to the same table.

### Relationship Structure (BEFORE)
```
User (1) ──────┬──────> TaskShare (Many)
              │
              └─> Multiple FK paths:
                  • user_id (user receiving share)
                  • created_by (user who created share)
                  [SQLAlchemy confused!]
```

---

## Solution Applied

### 1. Updated User Model (`app/models/user.py`)

**BEFORE**:
```python
task_shares = relationship(
    "TaskShare",
    back_populates="user",
    cascade="all, delete-orphan",
)
# Problem: Doesn't specify which foreign key to use!
```

**AFTER**:
```python
# Relationship 1: Tasks shared WITH this user (received shares)
task_shares = relationship(
    "TaskShare",
    back_populates="user",
    foreign_keys="TaskShare.user_id",  # ← EXPLICITLY specify FK
    cascade="all, delete-orphan",
)

# Relationship 2: Tasks shared BY this user (created shares)
shared_tasks = relationship(
    "TaskShare",
    back_populates="shared_by",
    foreign_keys="TaskShare.created_by",  # ← EXPLICITLY specify FK
    cascade="all, delete-orphan",
)
```

**Why This Works**:
- `task_shares`: Uses `user_id` FK - represents tasks shared WITH the user
- `shared_tasks`: Uses `created_by` FK - represents tasks shared BY the user
- Both are explicit, no ambiguity!

### 2. Updated TaskShare Model (`app/models/task_share.py`)

**BEFORE**:
```python
user = relationship("User", back_populates="task_shares", foreign_keys=[user_id])
shared_by = relationship("User", foreign_keys=[created_by])
# Problem: shared_by doesn't have back_populates
```

**AFTER**:
```python
user = relationship(
    "User",
    back_populates="task_shares",
    foreign_keys=[user_id],
)
shared_by = relationship(
    "User",
    back_populates="shared_tasks",  # ← Now references User.shared_tasks
    foreign_keys=[created_by],
)
```

**Why This Works**:
- `user`: References `User.task_shares` and uses `user_id` FK
- `shared_by`: References `User.shared_tasks` and uses `created_by` FK
- All relationships are bidirectional and explicit

---

## Relationship Diagram (AFTER)

```
User                          TaskShare
├── id                        ├── id
├── email                     ├── task_id → Task.id
├── full_name                 ├── user_id → User.id (⬅ task_shares)
│                            ├── created_by → User.id (⬅ shared_tasks)
├── tasks                     ├── role
│  └─> Task (owner_id)       └── shared_at
│
├── task_shares
│  └─> TaskShare (user_id)   "Tasks shared WITH me"
│
└── shared_tasks
   └─> TaskShare (created_by) "Tasks shared BY me"
```

---

## SQLAlchemy Pattern Applied

This follows the **SQLAlchemy best practice for multiple relationships to the same table**:

```python
# When a model has multiple FKs to the same related model:
# 1. Always specify foreign_keys=[] argument
# 2. Use different relationship names
# 3. Ensure back_populates is bidirectional
# 4. Add clear docstrings

class Parent(Base):
    fk_1 = Column(FK('child.id'))
    fk_2 = Column(FK('child.id'))

    rel_1 = relationship("Child", foreign_keys=[fk_1], back_populates="parent_1")
    rel_2 = relationship("Child", foreign_keys=[fk_2], back_populates="parent_2")

class Child(Base):
    parent_1 = relationship("Parent", foreign_keys=[Parent.fk_1])
    parent_2 = relationship("Parent", foreign_keys=[Parent.fk_2])
```

---

## Updated Model Relationships

### User Model Relationships

| Relationship | Type | Foreign Key | Purpose |
|---|---|---|---|
| `tasks` | One-to-Many | `Task.owner_id` | Tasks owned by user |
| `task_shares` | One-to-Many | `TaskShare.user_id` | Tasks shared WITH user |
| `shared_tasks` | One-to-Many | `TaskShare.created_by` | Tasks shared BY user |

### Task Model Relationships

| Relationship | Type | Foreign Key | Purpose |
|---|---|---|---|
| `owner` | Many-to-One | `Task.owner_id` | User who owns task |
| `task_shares` | One-to-Many | `TaskShare.task_id` | All shares for this task |

### TaskShare Model Relationships

| Relationship | Type | Foreign Key | Purpose |
|---|---|---|---|
| `task` | Many-to-One | `TaskShare.task_id` | The shared task |
| `user` | Many-to-One | `TaskShare.user_id` | User receiving share |
| `shared_by` | Many-to-One | `TaskShare.created_by` | User who created share |

---

## Files Modified

### 1. `backend/app/models/user.py`
- Added `foreign_keys="TaskShare.user_id"` to `task_shares` relationship
- Added `foreign_keys="TaskShare.created_by"` to `shared_tasks` relationship
- Updated docstring to document both share relationships

### 2. `backend/app/models/task_share.py`
- Added `back_populates="shared_tasks"` to `shared_by` relationship
- Ensured all `foreign_keys=[]` arguments are properly formatted
- Made relationships more explicit and readable

---

## Verification

### ✅ Models Load Without Errors
```python
from app.models.user import User
from app.models.task import Task
from app.models.task_share import TaskShare
# Success!
```

### ✅ Database Session Creates Successfully
```python
from app.database.session import engine, SessionLocal
# Success! No AmbiguousForeignKeysError
```

### ✅ FastAPI App Initializes
```python
from app.main import app
# Success! App ready to run
```

---

## Usage Example

### Accessing User's Shared Tasks

```python
from app.database.session import SessionLocal
from app.models.user import User

db = SessionLocal()

# Get a user
user = db.query(User).filter(User.id == user_id).first()

# Access tasks this user received shares for
received_shares = user.task_shares  # TaskShare objects for tasks shared WITH this user
for share in received_shares:
    print(f"Task: {share.task.title}, Role: {share.role}")

# Access tasks this user shared
shared = user.shared_tasks  # TaskShare objects for tasks shared BY this user
for share in shared:
    print(f"Shared '{share.task.title}' with {share.user.email} as {share.role}")
```

---

## Key Takeaway

**When a model has multiple foreign keys to the same related model, always explicitly specify `foreign_keys=[]` in the relationship() call.**

This prevents SQLAlchemy ambiguity errors and makes the code more maintainable and clear.

---

## Status

| Item | Status |
|------|--------|
| Error Identified | ✅ |
| Root Cause Found | ✅ |
| Solution Applied | ✅ |
| Models Updated | ✅ |
| Tests Passed | ✅ |
| Documentation Complete | ✅ |

---

## Reference

- **SQLAlchemy Docs**: [Explicit Foreign Keys in Relationships](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html)
- **Error Type**: `sqlalchemy.exc.AmbiguousForeignKeysError`
- **Solution Pattern**: Multiple relationships to same table with explicit foreign_keys

---

## Ready to Run

Backend is now ready to start:

```bash
cd backend
uv run uvicorn app.main:app --reload
```

All model relationships are now properly configured! 🎉
