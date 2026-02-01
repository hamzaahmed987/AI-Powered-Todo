---
description: "Task list for todo-cli feature implementation"
---

# Tasks: Command-Line Todo Application

**Input**: Design documents from `specs/001-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks included (Test-Driven Development approach per specification requirement: "All business logic must be unit testable")

**Organization**: Tasks are grouped by phase and user story to enable independent implementation and testing of each feature. Each user story phase is independently testable and can be deployed as an MVP increment.

## Format: `[ID] [P?] [Story] Description`

- **[ID]**: Sequential task ID (T001, T002, etc.) in execution order
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/todo_cli/`, `tests/` at repository root
- Paths shown below use standard structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Deliverables**:
- ✅ UV project initialized with Python 3.13+
- ✅ Directory structure created
- ✅ Dependencies configured (pytest, ruff, mypy)
- ✅ Entry point configured

---

### Setup Tasks

- [ ] T001 Create `pyproject.toml` with project metadata and dependencies configured for Python 3.13+, UV package manager, test runner (pytest), linter (ruff), and type checker (mypy)
- [ ] T002 [P] Create `src/todo_cli/__init__.py` with version metadata and package docstring
- [ ] T002 [P] Create `src/todo_cli/__main__.py` as entry point for `python -m todo_cli`
- [ ] T003 [P] Create `src/todo_cli/main.py` with `main()` function that instantiates and runs TodoCLI
- [ ] T004 [P] Create `tests/__init__.py` (test package marker)
- [ ] T005 [P] Create `README.md` with project overview, installation instructions, usage examples, and feature list
- [ ] T006 [P] Create `.gitignore` with Python standard entries (__pycache__, venv, .venv, *.pyc, *.egg-info, .pytest_cache, .mypy_cache, .ruff_cache)
- [ ] T007 Run `uv sync` to install all dependencies
- [ ] T008 Verify project setup: Run `uv run python -c "import src.todo_cli; print('Import successful')"` - should succeed

**Checkpoint**: Foundation ready - all files created, dependencies installed, project structure established

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and storage infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Data Model & Storage Layer

These are the core building blocks needed by all user stories (add, delete, update, list, complete all depend on Task model and storage).

#### Task Model Tests (Test-First)

- [ ] T009 [P] Create `tests/test_models.py` with test suite for Task dataclass including:
  - test_task_creation_with_valid_description: Creates task with id, description, completed=False, auto-generated created_at
  - test_task_rejects_empty_description: Task("") raises ValueError
  - test_task_rejects_whitespace_only_description: Task("   ") raises ValueError
  - test_task_rejects_description_over_200_chars: Task("x" * 201) raises ValueError
  - test_task_accepts_200_char_description: Task("x" * 200) succeeds
  - test_task_trims_whitespace_from_description: Task("  text  ") stores as "text"
  - test_task_default_values: Task(id=1, description="test").completed == False and created_at is set

#### Task Model Implementation

- [ ] T010 Create `src/todo_cli/models.py` with Task dataclass:
  - Fields: id (int), description (str), completed (bool = False), created_at (datetime = field(default_factory=datetime.now))
  - __post_init__ validation: non-empty, ≤200 chars, trim whitespace
  - All parameters and returns have type hints
  - Docstring for class and __post_init__

#### TaskStore Tests (Test-First)

- [ ] T011 [P] Create `tests/test_store.py` with test suite for TaskStore including:
  - test_add_creates_task_with_next_id: store.add("desc") returns Task with id=1, then id=2
  - test_add_increments_next_id_sequentially: Multiple adds produce sequential IDs
  - test_get_returns_task_or_none: store.get(1) returns Task, store.get(999) returns None
  - test_get_all_returns_tasks_in_order: All tasks returned sorted by ID
  - test_update_changes_description: store.update(1, "new") returns updated Task
  - test_update_returns_none_for_missing_id: store.update(999, "new") returns None
  - test_update_rejects_empty_description: store.update(1, "") raises ValueError
  - test_delete_removes_task_and_returns_true: store.delete(1) returns True, task no longer in store
  - test_delete_returns_false_for_missing_id: store.delete(999) returns False
  - test_mark_complete_sets_completed_flag: store.mark_complete(1) returns Task with completed=True
  - test_mark_complete_is_idempotent: Calling twice doesn't change result
  - test_mark_complete_returns_none_for_missing_id: store.mark_complete(999) returns None

#### TaskStore Implementation

- [ ] T012 Create `src/todo_cli/store.py` with TaskStore class:
  - Fields: _tasks (dict[int, Task]), _next_id (int = 1)
  - Methods: add(description: str) -> Task, get(task_id: int) -> Task | None, get_all() -> list[Task]
  - Methods: update(task_id: int, description: str) -> Task | None, delete(task_id: int) -> bool
  - Methods: mark_complete(task_id: int) -> Task | None
  - All parameters and returns have type hints
  - Docstring for all public methods

**Checkpoint**: Foundation ready - all tests pass, models and storage working, user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with descriptions, with unique sequential IDs

**Independent Test**: Can be fully tested by running add command with various descriptions and verifying task appears in list with unique ID and completed=False

### Tests for User Story 1 (Test-First)

- [ ] T013 [P] [US1] Create `tests/test_commands.py` with TodoCommands add command tests:
  - test_add_creates_task_successfully: commands.add("Buy groceries") returns success=True, message with ID
  - test_add_returns_task_data: CommandResult.data contains created Task
  - test_add_rejects_empty_description: commands.add("") returns success=False with error message
  - test_add_rejects_whitespace_only: commands.add("   ") returns error
  - test_add_rejects_over_200_chars: commands.add("x"*201) returns error
  - test_add_error_messages_match_spec: Error messages match specification exactly

- [ ] T014 [P] [US1] Create `tests/test_cli.py` with TodoCLI add command tests:
  - test_cli_add_parses_description: CLI._process_input("add Buy groceries") calls commands.add
  - test_cli_add_displays_success_message: Success message printed with task ID
  - test_cli_add_displays_error_for_empty: Error displayed for empty description

### Implementation for User Story 1

- [ ] T015 [P] [US1] Create CommandResult dataclass in `src/todo_cli/commands.py`:
  - Fields: success (bool), message (str), data (Any = None)
  - Docstring for class and all fields

- [ ] T016 [P] [US1] Create TodoCommands class in `src/todo_cli/commands.py`:
  - __init__(store: TaskStore) saves store as _store
  - add(description: str) -> CommandResult validates and creates task
  - Returns CommandResult(success=True, message=f"Task added successfully (ID: {id})", data=task) on success
  - Returns CommandResult(success=False, message="Error: ...") on validation failure
  - Docstring for class and add method

- [ ] T017 [US1] Implement TodoCLI class foundation in `src/todo_cli/cli.py`:
  - __init__() initializes TaskStore, TodoCommands, running flag
  - _process_input(user_input) parses command and routes to handlers
  - _handle_add(args) calls commands.add and displays result
  - _display_result(result) prints success/error with appropriate prefix (✓/✗)
  - Docstring for all methods

- [ ] T018 [US1] Implement REPL loop in TodoCLI.run():
  - Print welcome message
  - Loop: read input, process, handle KeyboardInterrupt and EOFError
  - Docstring

- [ ] T019 [US1] Implement TodoCLI._process_input() routing:
  - Parse command (first word), args (remainder)
  - Route to _handle_add, _handle_delete, _handle_update, _handle_list, _handle_complete, help, exit
  - Print "Unknown command" for unrecognized commands

**Checkpoint**: User Story 1 fully functional - users can add tasks and see confirmation with ID

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can see all tasks with their IDs, descriptions, and completion status in a formatted list

**Independent Test**: Can be fully tested by adding multiple tasks with different statuses and listing them; formatting correct with IDs, descriptions, and status shown

### Tests for User Story 2 (Test-First)

- [ ] T020 [P] [US2] Extend `tests/test_commands.py` with list_all command tests:
  - test_list_all_returns_empty_message: commands.list_all() returns message about no tasks
  - test_list_all_returns_tasks: After adding tasks, list_all returns data=[] or data=[tasks]
  - test_list_all_maintains_order: Tasks returned in ID order

- [ ] T021 [P] [US2] Extend `tests/test_cli.py` with list command tests:
  - test_cli_list_calls_list_all: CLI._process_input("list") calls commands.list_all()
  - test_cli_list_displays_table: _display_tasks() formats tasks in table with ID | Description | Status
  - test_cli_list_shows_empty_message: No tasks shows "No tasks found" message

### Implementation for User Story 2

- [ ] T022 [P] [US2] Implement TodoCommands.list_all() in `src/todo_cli/commands.py`:
  - Calls self._store.get_all()
  - Returns CommandResult(success=True, message="No tasks found...", data=[]) if empty
  - Returns CommandResult(success=True, message=f"Found {len(tasks)} task(s)", data=tasks) if tasks exist
  - Docstring

- [ ] T023 [US2] Implement TodoCLI._handle_list() in `src/todo_cli/cli.py`:
  - Calls commands.list_all()
  - If data exists, calls _display_tasks(data)
  - If no data, prints message

- [ ] T024 [US2] Implement TodoCLI._display_tasks() in `src/todo_cli/cli.py`:
  - Formats tasks in table: ID | Description | Status
  - Header row with column titles
  - Separator row with dashes
  - Data rows with task ID, description (truncated to 50 chars), status "[✓] Done" or "[ ] Todo"
  - Docstring

**Checkpoint**: User Stories 1 & 2 functional - users can add tasks and view them in formatted list

---

## Phase 5: User Story 3 - Mark Task as Complete (Priority: P1)

**Goal**: Users can mark tasks as completed by ID, with feedback for already-completed tasks

**Independent Test**: Can be fully tested by adding task, completing it, verifying status in list, attempting to complete again and getting info message

### Tests for User Story 3 (Test-First)

- [ ] T025 [P] [US3] Extend `tests/test_commands.py` with complete command tests:
  - test_complete_marks_task_done: commands.complete(1) returns success=True, message about completion
  - test_complete_sets_completed_flag: After complete(1), store.get(1).completed == True
  - test_complete_already_complete_returns_info: Completing task twice returns success=True with "is already complete" message
  - test_complete_nonexistent_task_returns_error: commands.complete(999) returns success=False with error

- [ ] T026 [P] [US3] Extend `tests/test_cli.py` with complete command tests:
  - test_cli_complete_parses_id: CLI._process_input("complete 1") extracts ID 1
  - test_cli_complete_invalid_id_shows_error: CLI._process_input("complete abc") shows error
  - test_cli_complete_missing_id_shows_error: CLI._process_input("complete") shows usage

### Implementation for User Story 3

- [ ] T027 [P] [US3] Implement TodoCommands.complete() in `src/todo_cli/commands.py`:
  - Gets task from store by task_id
  - Returns error if task not found
  - Returns info message if already completed (success=True with message "is already complete")
  - Calls store.mark_complete(task_id), returns success with message "marked as complete"
  - Docstring

- [ ] T028 [US3] Implement TodoCLI._parse_id() in `src/todo_cli/cli.py`:
  - Parses integer from string argument
  - Returns None and prints error if invalid or missing
  - Docstring

- [ ] T029 [US3] Implement TodoCLI._handle_complete() in `src/todo_cli/cli.py`:
  - Calls _parse_id() to get task_id
  - Calls commands.complete(task_id)
  - Calls _display_result(result)
  - Docstring

**Checkpoint**: User Stories 1, 2 & 3 fully functional - MVP complete! Users can add, view, and complete tasks

---

## Phase 6: User Story 4 - Update Task Description (Priority: P2)

**Goal**: Users can change task descriptions by ID without affecting completion status

**Independent Test**: Can be fully tested by adding task, updating description, verifying change in list, verifying completed status unchanged

### Tests for User Story 4 (Test-First)

- [ ] T030 [P] [US4] Extend `tests/test_commands.py` with update command tests:
  - test_update_changes_description: commands.update(1, "new desc") succeeds and returns updated Task
  - test_update_preserves_completed_status: After updating, completed status unchanged
  - test_update_rejects_empty_description: commands.update(1, "") returns error
  - test_update_rejects_over_200_chars: commands.update(1, "x"*201) returns error
  - test_update_nonexistent_task_returns_error: commands.update(999, "desc") returns error

- [ ] T031 [P] [US4] Extend `tests/test_cli.py` with update command tests:
  - test_cli_update_parses_id_and_description: CLI._process_input("update 1 new desc") extracts ID 1, description "new desc"
  - test_cli_update_missing_arguments_shows_error: CLI._process_input("update 1") shows usage error
  - test_cli_update_invalid_id_shows_error: CLI._process_input("update abc new") shows error

### Implementation for User Story 4

- [ ] T032 [P] [US4] Implement TodoCommands.update() in `src/todo_cli/commands.py`:
  - Validates task_id exists
  - Validates new description (non-empty, ≤200 chars)
  - Calls store.update(task_id, description)
  - Returns success or error CommandResult
  - Docstring

- [ ] T033 [US4] Implement TodoCLI._handle_update() in `src/todo_cli/cli.py`:
  - Parses arguments: task_id and multi-word description
  - Calls _parse_id() for task_id
  - Calls commands.update(task_id, description)
  - Calls _display_result(result)
  - Handles missing arguments with error message
  - Docstring

**Checkpoint**: User Stories 1-4 complete - users can add, view, complete, and update tasks

---

## Phase 7: User Story 5 - Delete Task (Priority: P2)

**Goal**: Users can remove tasks by ID with confirmation

**Independent Test**: Can be fully tested by adding task, deleting it, verifying it's gone from list

### Tests for User Story 5 (Test-First)

- [ ] T034 [P] [US5] Extend `tests/test_commands.py` with delete command tests:
  - test_delete_removes_task: commands.delete(1) returns success=True
  - test_delete_task_not_in_store: After delete(1), store.get(1) returns None
  - test_delete_nonexistent_task_returns_error: commands.delete(999) returns success=False with error

- [ ] T035 [P] [US5] Extend `tests/test_cli.py` with delete command tests:
  - test_cli_delete_parses_id: CLI._process_input("delete 1") extracts ID 1
  - test_cli_delete_invalid_id_shows_error: CLI._process_input("delete abc") shows error
  - test_cli_delete_missing_id_shows_error: CLI._process_input("delete") shows usage

### Implementation for User Story 5

- [ ] T036 [P] [US5] Implement TodoCommands.delete() in `src/todo_cli/commands.py`:
  - Calls store.delete(task_id)
  - Returns success if deleted, error if not found
  - Docstring

- [ ] T037 [US5] Implement TodoCLI._handle_delete() in `src/todo_cli/cli.py`:
  - Calls _parse_id() to get task_id
  - Calls commands.delete(task_id)
  - Calls _display_result(result)
  - Docstring

**Checkpoint**: All 5 user stories complete and independently testable

---

## Phase 8: User Experience & Help

**Goal**: Complete CLI experience with help command and exit

### Implementation

- [ ] T038 Implement TodoCLI.HELP_TEXT constant with all commands:
  - Lists: add, delete, update, list, complete, help, exit
  - Format: command name, description, example

- [ ] T039 Implement TodoCLI._process_input() help and exit cases:
  - "help" command prints HELP_TEXT
  - "exit" command sets running=False and prints "Goodbye!"
  - Docstring updates

- [ ] T040 [P] Create `tests/test_cli_help_exit.py` with help/exit tests:
  - test_help_command_displays_all_commands: help displays all 7 commands
  - test_exit_command_exits_loop: exit sets running=False
  - test_exit_displays_goodbye: "Goodbye!" printed

**Checkpoint**: Complete user experience with help and exit

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, testing, documentation

### Code Quality & Testing

- [ ] T041 [P] Run all unit tests: `uv run pytest tests/ -v` - verify all tests pass with >90% coverage
- [ ] T042 [P] Run linting: `uv run ruff check src/ tests/` - fix any violations
- [ ] T043 [P] Run type checking: `uv run mypy src/` - fix any type errors
- [ ] T044 Verify all docstrings present:
  - All public classes have docstring
  - All public methods have docstring with Args, Returns, Raises sections
  - All parameters and returns are type-hinted

### Documentation & Examples

- [ ] T045 Update `README.md` with complete sections:
  - Features list (add, delete, update, list, complete)
  - Installation: Python 3.13+, UV, `uv sync`
  - Usage: `uv run todo` command with example session
  - Commands table with syntax and examples
  - Development: pytest, ruff, mypy commands
  - License: MIT

### Integration Testing

- [ ] T046 Manual end-to-end workflow test: add 3 tasks → list → complete 1 → update 1 → delete 1 → list again
  - Verify IDs sequential (1, 2, 3)
  - Verify descriptions correct
  - Verify completion status displays correctly ([✓] for done, [ ] for todo)
  - Verify deletion removes task

- [ ] T047 Error scenario testing:
  - Try to add empty description → shows error
  - Try to complete non-existent task → shows error
  - Try to update with description > 200 chars → shows error
  - Try unknown command → shows help suggestion

- [ ] T048 Acceptance scenario validation (from spec.md):
  - All 18 acceptance scenarios from 5 user stories pass
  - Test at least one scenario per user story manually
  - Document results

### Final Validation

- [ ] T049 Final checklist:
  - [ ] All tests pass: `uv run pytest -v` ✓
  - [ ] No ruff errors: `uv run ruff check src tests` ✓
  - [ ] No mypy errors: `uv run mypy src` ✓
  - [ ] Application runs: `uv run todo` ✓
  - [ ] All 5 features work (add, delete, update, list, complete) ✓
  - [ ] Help displays correctly ✓
  - [ ] Exit works properly ✓
  - [ ] Error messages clear and helpful ✓
  - [ ] README accurate and complete ✓

**Checkpoint**: Production ready - all quality gates passed, documentation complete, ready for deployment

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phases 3-7 (User Stories)**: All depend on Phase 2 - can run in parallel or sequentially
  - US1 (Add): P1, foundational to all
  - US2 (List): P1, depends on US1 data existing
  - US3 (Complete): P1, depends on US1 data existing
  - US4 (Update): P2, can start after US2
  - US5 (Delete): P2, can start after US2
- **Phase 8 (UX/Help)**: Depends on Phases 3-7 - wraps up CLI
- **Phase 9 (Polish)**: Depends on all previous - final validation

### User Story Dependencies

- **US1 (Add)**: No dependencies on other stories (creates initial data)
- **US2 (List)**: Depends on US1 (data must exist to display)
- **US3 (Complete)**: Depends on US1 (tasks must exist to complete)
- **US4 (Update)**: Depends on US1, US2 (tasks must exist, results visible in list)
- **US5 (Delete)**: Depends on US1, US2 (tasks must exist, results visible in list)

### Within Each Phase

- **Test-First**: Write tests before implementation
- **Models before Services**: Data structures before logic
- **Services before CLI**: Business logic before user interface
- **Validation before Operations**: Check inputs before modifying state

### Parallel Opportunities

**Phase 1**: All tasks can run in parallel (different files, no dependencies)

**Phase 2**:
- T009-T012 can be partly parallel: T009 & T011 (tests) can write in parallel with T010 & T012 (implementations)

**User Stories (Phases 3-7)**:
- **Within Phase 3 (US1)**: T013-T014 (tests) parallel with T015-T019 (implementation)
- **Between Stories**: US4 (Update) and US5 (Delete) can run in parallel after Phase 2 (don't depend on each other)
- Different developers can work on different user stories simultaneously after Phase 2

### Sequential Within Phase Must Complete

- Write tests first (must define behavior)
- Implement production code (must pass tests)
- Verify integration with previous stories (ensures no breaking changes)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

To deliver MVP quickly:

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T012)
3. Complete Phase 3: User Story 1 (T013-T019)
4. **STOP and VALIDATE**: Test US1 independently - users can add tasks
5. Can demo/deploy at this point if needed

### Incremental Delivery (MVP + Features)

1. Complete Phases 1-2: Foundation (T001-T012)
2. Add Phase 3: User Story 1 → Test independently → Can deploy
3. Add Phase 4: User Story 2 → Test independently → Deploy (MVP+List)
4. Add Phase 5: User Story 3 → Test independently → Deploy (MVP+Complete)
5. Add Phase 6: User Story 4 → Test independently → Deploy
6. Add Phase 7: User Story 5 → Test independently → Deploy (Full Feature)
7. Polish (Phase 9): Code quality, docs → Final release

**Each story adds value without breaking previous stories**

### Parallel Team Strategy (If Multiple Developers)

With 5 developers available:

1. Developer A: Phase 1-2 (Setup & Foundational)
2. After Phase 2 complete, launch in parallel:
   - Developer B: Phase 3 (User Story 1 - Add)
   - Developer C: Phase 4 (User Story 2 - List)
   - Developer D: Phase 5 (User Story 3 - Complete)
   - Developer E: Phase 6 (User Story 4 - Update)
3. Phase 7 (Delete) can overlap with Phase 6
4. Merge and test together in Phase 8
5. Polish together in Phase 9

**With serial development**: Phases 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

---

## Notes

- [P] tasks = different files, no inter-dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Tests written BEFORE implementation (test-first approach)
- Each user story independently completable and testable
- Verify tests FAIL before implementing (TDD discipline)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
