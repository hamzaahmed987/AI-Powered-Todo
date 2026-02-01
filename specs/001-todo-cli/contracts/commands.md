# Command Contracts: Todo-CLI

**Feature**: 001-todo-cli | **Date**: 2025-12-05 | **Phase**: 1 (Design)

## Overview

This document defines the command interface contract for the todo-cli application. Each contract specifies input, output, validation rules, and error cases.

---

## Command: add

### Contract

Add a new task to the todo list.

### Signature

```python
def add(description: str) -> CommandResult:
    """Add a new task with given description."""
```

### Input

- **description** (str): Task description to add
  - Required: Yes
  - Constraints: 1-200 characters (trimmed)
  - Type: str

### Output

**Success**:
```python
CommandResult(
    success=True,
    message="✓ Task added successfully (ID: 1)",
    data=Task(id=1, description="...", completed=False, created_at=...)
)
```

**Failure**:
```python
CommandResult(
    success=False,
    message="✗ Error: Description cannot be empty"  # or other error
)
```

### Validation Rules

1. Description must not be empty (after trimming whitespace)
   - Error: `"Error: Description cannot be empty"`

2. Description must not exceed 200 characters
   - Error: `"Error: Description must not exceed 200 characters"`

### Side Effects

- Creates new Task in TaskStore with next sequential ID
- Increments TaskStore._next_id
- Task stored in TaskStore._tasks

### Error Cases

| Input | Expected Error |
|-------|-----------------|
| Empty string `""` | "Error: Description cannot be empty" |
| Only whitespace `"   "` | "Error: Description cannot be empty" |
| 201+ characters | "Error: Description must not exceed 200 characters" |

### Examples

```python
# Success
result = commands.add("Buy groceries")
# result.success = True
# result.data.id = 1
# result.data.description = "Buy groceries"

# Failure: empty
result = commands.add("")
# result.success = False
# result.message = "Error: Description cannot be empty"

# Failure: too long
result = commands.add("x" * 201)
# result.success = False
# result.message = "Error: Description must not exceed 200 characters"
```

---

## Command: delete

### Contract

Delete a task by ID.

### Signature

```python
def delete(task_id: int) -> CommandResult:
    """Delete task with given ID."""
```

### Input

- **task_id** (int): ID of task to delete
  - Required: Yes
  - Type: int
  - Constraints: Must be positive integer

### Output

**Success**:
```python
CommandResult(
    success=True,
    message="✓ Task 1 deleted successfully"
)
```

**Failure**:
```python
CommandResult(
    success=False,
    message="✗ Error: Task with ID 999 not found"  # or other error
)
```

### Validation Rules

1. task_id must be an integer
   - Error (from CLI layer): `"Error: Please provide a valid task ID (number)"`

2. task_id must exist in store
   - Error: `"Error: Task with ID [N] not found"`

### Side Effects

- Removes Task from TaskStore._tasks
- Task no longer retrievable
- ID is not reused

### Error Cases

| Input | Expected Error |
|-------|-----------------|
| Non-existent ID (999) | "Error: Task with ID 999 not found" |
| Non-integer (from CLI) | "Error: Please provide a valid task ID (number)" |

### Examples

```python
# Success
commands.add("Task 1")  # Creates Task with id=1
result = commands.delete(1)
# result.success = True
# result.message = "✓ Task 1 deleted successfully"

# Failure: not found
result = commands.delete(999)
# result.success = False
# result.message = "Error: Task with ID 999 not found"
```

---

## Command: update

### Contract

Update a task's description by ID.

### Signature

```python
def update(task_id: int, description: str) -> CommandResult:
    """Update task description."""
```

### Input

- **task_id** (int): ID of task to update
  - Required: Yes
  - Type: int

- **description** (str): New description
  - Required: Yes
  - Constraints: 1-200 characters (trimmed)
  - Type: str

### Output

**Success**:
```python
CommandResult(
    success=True,
    message="✓ Task 1 updated successfully",
    data=Task(id=1, description="new desc", ...)
)
```

**Failure**:
```python
CommandResult(
    success=False,
    message="✗ Error: Task with ID 999 not found"  # or other error
)
```

### Validation Rules

1. task_id must exist
   - Error: `"Error: Task with ID [N] not found"`

2. description must not be empty (after trim)
   - Error: `"Error: Description cannot be empty"`

3. description must not exceed 200 characters
   - Error: `"Error: Description must not exceed 200 characters"`

### Side Effects

- Modifies Task.description
- Task.id and Task.created_at unchanged
- Task.completed status unchanged

### Error Cases

| Input | Expected Error |
|-------|-----------------|
| Non-existent ID | "Error: Task with ID [N] not found" |
| Empty description | "Error: Description cannot be empty" |
| Description > 200 chars | "Error: Description must not exceed 200 characters" |

### Examples

```python
# Success
commands.add("Old description")  # id=1
result = commands.update(1, "New description")
# result.success = True
# result.message = "✓ Task 1 updated successfully"
# result.data.description = "New description"

# Failure: not found
result = commands.update(999, "Something")
# result.success = False
# result.message = "Error: Task with ID 999 not found"
```

---

## Command: list_all

### Contract

List all tasks in the todo list.

### Signature

```python
def list_all(self) -> CommandResult:
    """Get all tasks."""
```

### Input

None.

### Output

**With Tasks**:
```python
CommandResult(
    success=True,
    message="Tasks:",
    data=[Task(...), Task(...), ...]  # List of all tasks
)
```

**Empty List**:
```python
CommandResult(
    success=True,
    message="No tasks found. Add a task using 'add <description>'",
    data=[]
)
```

### Validation Rules

None (always succeeds).

### Side Effects

None (read-only).

### Error Cases

None (always returns CommandResult with success=True).

### Examples

```python
# With tasks
commands.add("Task 1")
commands.add("Task 2")
result = commands.list_all()
# result.success = True
# result.data = [Task(id=1, ...), Task(id=2, ...)]

# Empty
result = commands.list_all()
# result.success = True
# result.message = "No tasks found. Add a task using 'add <description>'"
# result.data = []
```

---

## Command: complete

### Contract

Mark a task as completed.

### Signature

```python
def complete(task_id: int) -> CommandResult:
    """Mark task as completed."""
```

### Input

- **task_id** (int): ID of task to mark complete
  - Required: Yes
  - Type: int

### Output

**Success (Task Was Incomplete)**:
```python
CommandResult(
    success=True,
    message="✓ Task 1 marked as complete",
    data=Task(id=1, ..., completed=True)
)
```

**Already Complete**:
```python
CommandResult(
    success=True,
    message="ℹ Task 1 is already complete",
    data=Task(id=1, ..., completed=True)
)
```

**Failure**:
```python
CommandResult(
    success=False,
    message="✗ Error: Task with ID 999 not found"  # or other error
)
```

### Validation Rules

1. task_id must be an integer
   - Error (from CLI layer): `"Error: Please provide a valid task ID (number)"`

2. task_id must exist
   - Error: `"Error: Task with ID [N] not found"`

3. If task already complete, return info message (not error)
   - Message: `"ℹ Task [N] is already complete"`

### Side Effects

- Sets Task.completed = True
- Idempotent (can call multiple times safely)

### Error Cases

| Input | Expected Response |
|-------|-------------------|
| Non-existent ID | success=False, "Error: Task with ID [N] not found" |
| Already complete ID | success=True, "ℹ Task [N] is already complete" |

### Examples

```python
# Success
commands.add("Task 1")  # completed=False
result = commands.complete(1)
# result.success = True
# result.message = "✓ Task 1 marked as complete"
# result.data.completed = True

# Idempotent: already complete
result = commands.complete(1)
# result.success = True
# result.message = "ℹ Task 1 is already complete"
# result.data.completed = True (unchanged)

# Failure: not found
result = commands.complete(999)
# result.success = False
# result.message = "Error: Task with ID 999 not found"
```

---

## CommandResult Contract

### Signature

```python
@dataclass
class CommandResult:
    success: bool
    message: str
    data: Any = None
```

### Fields

- **success** (bool): Whether command executed successfully
- **message** (str): Human-readable message to display to user
- **data** (Any): Command-specific data (Task, list of Tasks, or None)

### Usage

- CLI layer calls commands and receives CommandResult
- CLI always displays message
- CLI displays data if present (e.g., table of tasks)
- All commands return CommandResult (never raise exceptions to CLI)

---

## Error Message Format Convention

### Success Messages

- Prefix: `"✓ "` (check mark)
- Format: `"✓ Task added successfully (ID: 1)"`

### Error Messages

- Prefix: `"✗ "` (X mark)
- Format: `"✗ Error: [specific error]"`
- Examples:
  - `"✗ Error: Description cannot be empty"`
  - `"✗ Error: Task with ID 999 not found"`

### Info Messages

- Prefix: `"ℹ "` (info symbol)
- Format: `"ℹ [situation]"`
- Examples:
  - `"ℹ Task 1 is already complete"`

---

## Testing Strategy

For each command:

1. **Happy Path**: Valid inputs → success=True, correct message
2. **Boundary Cases**: Empty, max length, edge values
3. **Error Cases**: Non-existent IDs, invalid inputs
4. **Idempotency**: Operations that should be idempotent (complete, update same value)
5. **State Persistence**: After command, store state correct

Example test structure:

```python
def test_add_creates_task():
    """Test: add with valid description creates task."""
    commands = TodoCommands(TaskStore())
    result = commands.add("Buy groceries")

    assert result.success
    assert result.message == "✓ Task added successfully (ID: 1)"
    assert result.data.id == 1
    assert result.data.description == "Buy groceries"

def test_add_rejects_empty():
    """Test: add with empty description returns error."""
    commands = TodoCommands(TaskStore())
    result = commands.add("")

    assert not result.success
    assert "Description cannot be empty" in result.message
```
