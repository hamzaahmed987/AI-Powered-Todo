# Research: Python CLI Design Patterns & Best Practices

**Feature**: 001-todo-cli | **Date**: 2025-12-05 | **Phase**: 0 (Research)

## Overview

This document captures research findings on Python CLI design patterns, dataclass validation, in-memory storage, and testing strategies for a simple command-line todo application.

---

## 1. Python CLI Input Patterns

### Topic: Simple Input Loop vs CLI Frameworks

**Decision**: Use simple input loop with manual command parsing

**Rationale**:
- Constitution constraint: "DO NOT use complex frameworks for the CLI (argparse or simple input is sufficient)"
- YAGNI principle: No need for Click, Typer, or argparse for 5 simple commands
- Requirement is clarity, not sophistication
- Manual parsing gives complete control over error messages matching spec

**Pattern**:
```python
while running:
    user_input = input("> ").strip()
    parts = user_input.split(None, 2)  # Split on whitespace
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    # Route to handler based on command
```

**Alternatives Considered**:
- argparse: Overkill for 5 commands; adds boilerplate
- Click: Framework overhead; error messages not customizable to spec
- Typer: More overhead; same limitations as Click

---

## 2. Dataclass Validation

### Topic: Best Practices for Task Model Validation

**Decision**: Use `@dataclass` with `__post_init__` validation

**Rationale**:
- Python 3.10+ standard library feature (already available in 3.13+)
- Clean, readable, minimal boilerplate
- Type hints built-in
- Validation at instantiation time (fail-fast)

**Pattern**:
```python
@dataclass
class Task:
    id: int
    description: str
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate on creation."""
        if not self.description.strip():
            raise ValueError("Description cannot be empty")
        if len(self.description) > 200:
            raise ValueError("Description must not exceed 200 characters")
```

**Alternatives Considered**:
- Pydantic: Overkill; adds dependency; constitution says no external databases/persistence (implicit no heavy dependencies)
- Validation in TaskStore: Violates separation of concerns; store should trust model integrity
- Validation in CLI only: Allows invalid Task objects to exist; poor design

---

## 3. In-Memory Storage Patterns

### Topic: Storing and Retrieving Tasks Efficiently

**Decision**: Use `dict[int, Task]` with manual ID increment

**Rationale**:
- O(1) lookup by ID (requirement: < 100ms operations)
- dict preserves insertion order in Python 3.7+ (can iterate in creation order)
- Scales linearly to 10,000 tasks
- No external dependencies

**Pattern**:
```python
class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, description: str) -> Task:
        task = Task(id=self._next_id, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task
```

**Alternatives Considered**:
- List[Task]: O(n) lookup by ID; requires linear search
- Pydantic models: Adds dependency; not needed for MVP
- File storage: Constitution says no persistence
- SQLite: Constitution says no databases

---

## 4. Error Handling Patterns

### Topic: User-Friendly Error Messages

**Decision**: Return `CommandResult` dataclass with structured success/message/data

**Rationale**:
- Separates error handling logic from display logic
- Enables testing error paths without mocking output
- Consistent format for all command results
- Allows CLI to format errors consistently

**Pattern**:
```python
@dataclass
class CommandResult:
    success: bool
    message: str
    data: Any = None

# In command handlers:
def add(self, description: str) -> CommandResult:
    try:
        description = description.strip()
        if not description:
            return CommandResult(False, "Error: Description cannot be empty")
        task = self.store.add(description)
        return CommandResult(True, f"✓ Task added successfully (ID: {task.id})", task)
    except ValueError as e:
        return CommandResult(False, f"✗ Error: {str(e)}")
```

**Alternatives Considered**:
- Raise exceptions in all layers: Couples CLI to internal errors; harder to test
- Print directly in commands: Violates separation of concerns
- HTTP-style status codes: Overkill for CLI; users prefer readable messages

---

## 5. Testing Patterns for Stateful Objects

### Topic: Unit Testing Classes with State

**Decision**: Inject dependencies (Store into Commands, Commands into CLI); use fixtures for state setup

**Rationale**:
- Allows isolated unit testing of each layer
- Easy to verify behavior without side effects
- pytest fixtures keep tests clean

**Pattern**:
```python
# Fixture in conftest.py
@pytest.fixture
def store():
    return TaskStore()

@pytest.fixture
def commands(store):
    return TodoCommands(store)

# Test
def test_add_creates_task_with_id(commands):
    result = commands.add("Buy groceries")
    assert result.success
    assert result.data.id == 1
    assert result.data.description == "Buy groceries"

# Next task increments ID
    result2 = commands.add("Walk dog")
    assert result2.data.id == 2
```

**Alternatives Considered**:
- Global state: Violates constitution ("No global mutable state")
- Mock objects: Unnecessary for simple in-memory store
- Integration tests only: Slower; harder to isolate failures

---

## 6. Table Display in Terminal

### Topic: Formatted Output for Task List

**Decision**: Use box-drawing characters (Unicode) with fixed-width formatting

**Rationale**:
- Professional appearance
- Works across Windows, macOS, Linux (modern terminals support Unicode)
- Easy to parse with fixed widths
- Matches specification example

**Pattern**:
```python
def display_tasks_table(self, tasks: list[Task]) -> None:
    # Calculate column widths
    id_width = 4
    desc_width = 20
    status_width = 10

    # Print header
    print(f"┌{'─' * (id_width + 2)}┬{'─' * (desc_width + 2)}┬{'─' * (status_width + 2)}┐")
    print(f"│ {'ID'.center(id_width)} │ {'Description'.center(desc_width)} │ {'Status'.center(status_width)} │")
    print(f"├{'─' * (id_width + 2)}┼{'─' * (desc_width + 2)}┼{'─' * (status_width + 2)}┤")

    # Print rows
    for task in tasks:
        status = "[✓] Done" if task.completed else "[ ] Todo"
        desc = task.description[:desc_width].ljust(desc_width)
        print(f"│ {str(task.id).center(id_width)} │ {desc} │ {status.center(status_width)} │")

    print(f"└{'─' * (id_width + 2)}┴{'─' * (desc_width + 2)}┴{'─' * (status_width + 2)}┘")
```

**Alternatives Considered**:
- Simple list output: Less user-friendly; harder to parse visually
- JSON output: Not CLI-friendly for end users
- Rich library: External dependency; not needed for simple formatting

---

## 7. Type Hints in Python 3.13+

### Topic: Modern Type Hint Syntax

**Decision**: Use PEP 585 union syntax (`Optional[T]`, `list[T]`, `dict[K, V]`)

**Rationale**:
- Python 3.13 supports modern syntax
- More readable than `Optional[T]` vs `Union[T, None]`
- Built-in generic types (`list`, `dict`) available since 3.9

**Pattern**:
```python
def get(self, task_id: int) -> Optional[Task]:
    return self._tasks.get(task_id)

def get_all(self) -> list[Task]:
    return list(self._tasks.values())

def add(self, description: str) -> Task:
    # Returns Task (not Optional)
```

**Note**: `Optional[T]` is `T | None` in 3.10+ but keeping `Optional` for clarity and mypy compatibility.

---

## 8. REPL Loop Design

### Topic: Main Input Loop Implementation

**Decision**: Simple while loop with exception handling for Ctrl+C and EOF

**Rationale**:
- Transparent to user
- Handles interrupts gracefully
- Minimal complexity
- Clear entry/exit points

**Pattern**:
```python
def run(self) -> None:
    self.running = True
    print("Welcome to todo-cli! Type 'help' for available commands.")
    while self.running:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue  # Skip empty input
            self.execute(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            self.running = False
        except EOFError:
            print("\nGoodbye!")
            self.running = False
```

---

## Summary of Decisions

| Decision | Pattern | Justification |
|----------|---------|--------------|
| Input parsing | Simple split() | Constitution constraint; minimal complexity |
| Models | @dataclass + __post_init__ | Type-safe, clean, standard library |
| Storage | dict[int, Task] | O(1) lookup, linear scaling, no dependencies |
| Error handling | CommandResult dataclass | Testable, structured, consistent |
| Testing | Dependency injection + fixtures | Isolated, unit testable per layer |
| Display | Unicode box drawing | Professional, readable, cross-platform |
| Type hints | Modern 3.13+ syntax | Clear, mypy-compatible, readable |
| REPL | while loop | Simple, transparent, handles interrupts |

All decisions align with the project constitution (no complex frameworks, clear code, unit testable, no external dependencies for runtime).
