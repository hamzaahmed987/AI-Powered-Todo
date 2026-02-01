# Data Model: Command-Line Todo Application

**Feature**: 001-todo-cli | **Date**: 2025-12-05 | **Phase**: 1 (Design)

## Entity: Task

### Definition

A task represents a single to-do item in the todo-cli application.

```python
@dataclass
class Task:
    id: int
    description: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

### Attributes

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `id` | `int` | ✓ Yes | N/A | Unique sequential identifier (auto-assigned by TaskStore) |
| `description` | `str` | ✓ Yes | N/A | User-provided task description (1-200 characters) |
| `completed` | `bool` | No | `False` | Whether the task is marked as done |
| `created_at` | `datetime` | No | `now()` | Timestamp of task creation (auto-assigned at instantiation) |

### Validation Rules

**ID**:
- Must be positive integer
- Assigned sequentially by TaskStore (1, 2, 3, ...)
- Must be unique within a session
- Immutable after creation

**Description**:
- Must not be empty (trimmed of whitespace)
- Must not exceed 200 characters
- Can contain any Unicode characters (special chars, emoji, etc.)
- Immutable after creation (updated via TaskStore.update, not direct mutation)

**Completed**:
- Boolean flag (True or False)
- Default: False (all new tasks start as incomplete)
- Can be changed via TaskStore.mark_complete()

**Created_at**:
- Timestamp when Task object was instantiated
- Set once, never changed
- Used for ordering (if needed in future)

### State Transitions

```
Task Creation
    ↓
[Task: id, description, completed=False, created_at=now()]
    ↓
    ├─ Complete: completed=False → completed=True
    │  (via TodoCommands.complete() → TaskStore.mark_complete())
    │
    ├─ Update Description: description changed
    │  (via TodoCommands.update() → TaskStore.update())
    │
    └─ Delete: Task removed from store
       (via TodoCommands.delete() → TaskStore.delete())
```

### Usage Examples

**Create a task**:
```python
store = TaskStore()
task = store.add("Buy groceries")
# task = Task(id=1, description="Buy groceries", completed=False, created_at=datetime.now())
```

**Mark complete**:
```python
store.mark_complete(1)
# task.completed = True
```

**Update description**:
```python
store.update(1, "Buy organic groceries")
# task.description = "Buy organic groceries"
```

**Retrieve all tasks**:
```python
all_tasks = store.get_all()
# Returns list of all Task objects in creation order
```

---

## Storage: TaskStore

### Definition

In-memory storage for all tasks with CRUD operations and ID auto-generation.

```python
class TaskStore:
    _tasks: dict[int, Task]
    _next_id: int
```

### Behavior

**Initialization**:
- Start with empty dict and next_id=1
- No persistence; all data lost on application exit

**Add**:
- Create new Task with next_id
- Store in dict at key=id
- Increment next_id
- Return created Task

**Get**:
- Return Task by ID or None if not found
- O(1) lookup time

**Get All**:
- Return list of all Tasks in creation order
- Order maintained by dict (Python 3.7+)

**Update**:
- Change Task description by ID
- Return updated Task or None if not found
- ID and created_at are immutable

**Delete**:
- Remove Task from dict by ID
- Return True if deleted, False if not found

**Mark Complete**:
- Set Task.completed = True by ID
- Return updated Task or None if not found
- Idempotent (can mark complete multiple times)

### Design Decisions

**Dictionary Storage**:
- `dict[int, Task]` chosen for O(1) lookup performance
- Requirement: < 100ms operations on up to 10,000 tasks
- Alternative of list would be O(n) lookup

**Sequential ID Generation**:
- Simplest approach: increment counter
- Avoids UUID complexity
- Meets requirement for "unique sequential ID"
- No gaps (IDs are 1, 2, 3, ...) unless deleted

**No Persistence**:
- Constitution requirement: "DO NOT use external databases or file storage"
- All tasks in memory only
- Lost on process exit

---

## Relationships

### Task → TaskStore
- One-to-Many: One TaskStore owns many Tasks
- Foreign Key: Task.id is primary key in TaskStore._tasks dict
- Dependency: TodoCommands depends on TaskStore to create/modify Tasks

### Task → TodoCommands
- One-to-Many: One TodoCommands operates on many Tasks via TaskStore
- TodoCommands never directly instantiates Tasks (only TaskStore does)
- TodoCommands provides business logic around Task operations

### TodoCommands → TodoCLI
- One-to-Many: One CLI invokes TodoCommands methods
- TodoCLI receives CommandResult and displays to user
- CLI never directly accesses Tasks

**Dependency Flow**:
```
TodoCLI
  ↓ invokes
TodoCommands
  ↓ uses
TaskStore
  ↓ manages
Task
```

---

## Constraints & Invariants

### Invariants (Must Always Be True)

1. **Unique IDs**: No two Tasks in store have same ID
2. **Sequential IDs**: If max ID is N, then IDs are {1, 2, ..., N} minus deleted IDs
3. **Valid Description**: All Tasks have non-empty, ≤200 char descriptions
4. **Store Consistency**: TaskStore._next_id > max(id in _tasks)
5. **Immutable Identity**: Task.id and Task.created_at never change

### Assumptions

1. Single-threaded: No concurrent access to TaskStore
2. Single-user: One user per application session
3. No persistence: Data exists only in memory during session
4. No undo/redo: Operations are final (no transaction rollback)

---

## Evolution & Migration

### Current Version

- Version: 1.0.0
- Date: 2025-12-05
- Status: Initial implementation

### Future Enhancements (Out of Scope)

If persistence is added later:
1. Write Task as JSON to file
2. Read Tasks from file on startup
3. Serialize datetime objects
4. Handle file conflicts/locking

Implementation notes:
- Current TaskStore interface (`add`, `get`, `get_all`, `update`, `delete`, `mark_complete`) is persistence-agnostic
- Could swap dict with database without changing TodoCommands
- Well-structured data layer enables future persistence

---

## Testing Strategy

### Unit Tests for Task

- Valid task creation
- Validation: empty description rejected
- Validation: >200 char description rejected
- Default values (completed=False, created_at set)
- Task immutability checks (id and created_at don't change)

### Unit Tests for TaskStore

- Add creates task with sequential IDs
- Get returns task or None
- Get all returns list in order
- Update modifies description
- Delete removes task
- Mark complete sets flag
- Edge cases (non-existent IDs, empty store)

### Integration Tests

- Add → Get → Update → Mark Complete → Delete full cycle
- Multiple tasks maintain state correctly
- ID generation handles deletions (no ID reuse)
