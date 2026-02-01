# Quick Start: Todo-CLI Development

**Feature**: 001-todo-cli | **Date**: 2025-12-05 | **For Developers**

## Project Setup

### Prerequisites

- Python 3.13+ installed
- UV package manager installed

### Initial Setup

```bash
# Clone the repository (already done)
cd Todo\ App

# Create virtual environment and install dependencies
uv sync

# Verify installation
python -m pytest --version
ruff --version
mypy --version
```

### Directory Structure

```
src/
└── todo_cli/           # Main package
    ├── __init__.py     # Package metadata
    ├── __main__.py     # Entry point (python -m todo_cli)
    ├── main.py         # Application startup
    ├── models.py       # Task dataclass
    ├── store.py        # TaskStore (CRUD operations)
    ├── commands.py     # TodoCommands (business logic)
    └── cli.py          # TodoCLI (REPL interface)

tests/
├── __init__.py
├── test_models.py      # Task validation tests
├── test_store.py       # TaskStore CRUD tests
├── test_commands.py    # Command handler tests
└── test_cli.py         # Integration tests
```

---

## Development Workflow

### 1. Run Tests

Before and after implementing each phase:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=src/

# Watch mode (requires pytest-watch)
ptw
```

### 2. Code Quality

Check code quality before committing:

```bash
# Lint code (PEP 8)
ruff check src/ tests/

# Fix common issues automatically
ruff check --fix src/ tests/

# Type checking
mypy src/

# Type checking with strict mode
mypy --strict src/
```

### 3. Running the Application

Once Phase 1-4 are complete:

```bash
# Run the application
python -m todo_cli

# In the REPL, try:
> help                    # Show available commands
> add Buy groceries
> list
> complete 1
> exit
```

---

## Implementation Phases Checklist

### Phase 1: Project Setup

- [ ] Create `pyproject.toml` with Python 3.13+, pytest, ruff, mypy
- [ ] Create `src/todo_cli/__init__.py` (empty or with version)
- [ ] Create `src/todo_cli/__main__.py` (entry point)
- [ ] Create `README.md` with overview
- [ ] Create `.gitignore` for Python
- [ ] Run `uv sync` successfully
- [ ] Verify `python -m todo_cli` imports (even if not functional yet)

**Verification**:
```bash
uv sync
python -c "import src.todo_cli; print('Import successful')"
```

### Phase 2: Data Model & Storage

- [ ] Create `src/todo_cli/models.py` with Task dataclass
  - Fields: id, description, completed, created_at
  - Validation in __post_init__ for description
- [ ] Create `src/todo_cli/store.py` with TaskStore class
  - Methods: add, get, get_all, update, delete, mark_complete
  - Use dict for storage, manual ID increment
- [ ] Create `tests/test_models.py` with Task tests
  - Test validation (empty, too long, valid)
  - Test defaults (completed=False, created_at auto)
- [ ] Create `tests/test_store.py` with TaskStore tests
  - Test CRUD operations
  - Test ID auto-increment
  - Test edge cases (non-existent IDs)
- [ ] Update `specs/001-todo-cli/data-model.md`

**Verification**:
```bash
pytest tests/test_models.py tests/test_store.py -v
mypy src/todo_cli/models.py src/todo_cli/store.py
ruff check src/todo_cli/models.py src/todo_cli/store.py
```

### Phase 3: Command Handlers

- [ ] Create `src/todo_cli/commands.py` with TodoCommands class
  - CommandResult dataclass for structured results
  - Methods: add, delete, update, list_all, complete
  - All with validation and error handling
- [ ] Create `tests/test_commands.py` with command tests
  - Test each command with valid inputs
  - Test error cases (non-existent IDs, validation failures)
  - Test error messages match spec
- [ ] Create `specs/001-todo-cli/contracts/commands.md`

**Verification**:
```bash
pytest tests/test_commands.py -v
mypy src/todo_cli/commands.py
ruff check src/todo_cli/commands.py
```

### Phase 4: CLI Interface

- [ ] Create `src/todo_cli/cli.py` with TodoCLI class
  - REPL loop: input → parse → execute → display
  - Methods: run, execute, parse_command, display_result, display_help
  - Table formatting for task list
- [ ] Create `src/todo_cli/main.py` with main() function
  - Instantiate TodoCLI and call run()
- [ ] Update `src/todo_cli/__main__.py` to call main()
- [ ] Create `tests/test_cli.py` with integration tests
  - Test command parsing
  - Test REPL flow
  - Test table display
- [ ] Create `specs/001-todo-cli/quickstart.md` (this file)

**Verification**:
```bash
pytest tests/test_cli.py -v
python -m todo_cli
# Then manually test: add, list, complete, delete, help, exit
mypy src/
ruff check src/
```

### Phase 5: Quality & Testing

- [ ] Run all tests and achieve > 90% coverage
  - `pytest --cov=src/`
- [ ] Fix any ruff violations
  - `ruff check --fix src/ tests/`
- [ ] Fix any mypy type errors
  - `mypy src/`
- [ ] Verify all public functions have docstrings
  - Check each .py file manually
- [ ] Update README.md with usage examples
  - Add example commands
  - Add expected output examples

**Verification**:
```bash
pytest --cov=src/
ruff check src/ tests/
mypy src/
```

### Phase 6: Integration & Documentation

- [ ] Manual end-to-end testing
  - Add 3 tasks
  - View list
  - Complete 1
  - Update 1
  - Delete 1
  - View list again
- [ ] Verify all 18 acceptance scenarios from spec.md pass
- [ ] Test error paths (invalid IDs, empty descriptions, etc.)
- [ ] Final documentation review
- [ ] Commit all changes
- [ ] Prepare for `/sp.tasks` phase

---

## Common Commands During Development

```bash
# Install/update dependencies
uv sync

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/

# Check code style
ruff check src/ tests/

# Fix code style issues
ruff check --fix src/ tests/

# Type check
mypy src/

# Run app
python -m todo_cli

# Run specific test
pytest tests/test_models.py::test_task_validation -v

# Run tests matching pattern
pytest -k "test_add" -v
```

---

## Debugging Tips

### Debugging a Test

Add print statements or use pdb:

```python
def test_add_creates_task():
    commands = TodoCommands(TaskStore())
    result = commands.add("Buy groceries")

    import pdb; pdb.set_trace()  # Breaks here
    assert result.success
```

Run with:
```bash
pytest tests/test_models.py::test_add_creates_task -v -s
```

### Type Checking Issues

If mypy complains about types:

```python
# Bad: mypy can't infer
result = commands.add("something")  # result type unclear

# Good: explicit type
result: CommandResult = commands.add("something")  # Type is clear
```

### Import Issues

If getting import errors, ensure:
1. `__init__.py` exists in each package directory
2. Running from repo root
3. Correct path in PYTHONPATH

```bash
# Verify imports
python -c "from src.todo_cli.models import Task; print(Task.__name__)"
```

---

## Testing Strategy Summary

### Unit Tests (By Phase)

**Phase 2 (Models & Storage)**:
- TaskStore CRUD operations
- Task validation
- ID auto-increment

**Phase 3 (Commands)**:
- Command logic
- Error message content
- Validation boundaries

**Phase 4 (CLI)**:
- Command parsing
- Table formatting
- REPL behavior

**Phase 5 (Integration)**:
- Full workflows
- Error recovery
- Edge cases

### Test Organization

```python
# Good: Clear test names
def test_add_creates_task_with_sequential_id():
    pass

def test_add_rejects_empty_description():
    pass

# Better: Use fixtures
@pytest.fixture
def store():
    return TaskStore()

def test_add_with_fixture(store):
    pass
```

---

## Git Workflow

```bash
# After each phase
git add -A
git commit -m "Implement Phase [N]: [Description]"

# Example commits:
# "Implement Phase 1: Project setup with pyproject.toml"
# "Implement Phase 2: Task model and TaskStore"
# "Implement Phase 3: Command handlers with validation"
# "Implement Phase 4: CLI REPL interface"
```

---

## Troubleshooting

### `python -m todo_cli` doesn't start

1. Check `src/todo_cli/__main__.py` exists
2. Check `src/todo_cli/main.py` has `main()` function
3. Check `src/todo_cli/cli.py` has `TodoCLI` class
4. Run `python -m todo_cli --help` for errors

### Tests fail with import errors

```bash
# Ensure you're in repo root
cd "E:\Panaversity Hackathon\Todo App"

# Run from root
python -m pytest tests/test_models.py
```

### mypy complains about types

```bash
# Check specific file
mypy src/todo_cli/models.py

# Get more detail
mypy src/todo_cli/models.py --show-error-codes
```

### ruff finds style issues

```bash
# See what's wrong
ruff check src/

# Auto-fix most issues
ruff check --fix src/

# Some require manual fixes
```

---

## Resources

- [Python docs](https://docs.python.org/3.13/)
- [pytest docs](https://docs.pytest.org/)
- [mypy docs](https://mypy.readthedocs.io/)
- [ruff docs](https://docs.astral.sh/ruff/)
- [PEP 8 Style Guide](https://pep8.org/)
