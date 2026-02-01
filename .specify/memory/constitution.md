<!-- Sync Impact Report
Version Change: (new file) → 1.0.0
Reason: Initial constitution establishment for Todo App CLI project
Principles Added:
  - Clean Code Standards (1 of 6)
  - Project Structure (2 of 6)
  - Development Methodology (3 of 6)
  - Data Management (4 of 6)
  - User Experience (5 of 6)
  - Code Quality Gates (6 of 6)
Additional Sections:
  - Constraints (non-negotiable project boundaries)
  - Success Criteria (definitive completion conditions)
  - Governance (amendment and compliance procedures)
Templates Requiring Updates: ✅ spec-template.md, ✅ plan-template.md, ✅ tasks-template.md
-->

# Todo App Constitution

## Core Principles

### 1. Clean Code Standards

Write readable, self-documenting code with meaningful variable and function names. Follow PEP 8 style guidelines strictly. Keep functions small and focused on a single responsibility. Use type hints for all function parameters and return values. Write docstrings for all public functions and classes.

**Rationale**: Clean, well-typed code reduces maintenance burden, improves onboarding, and prevents defects through explicitness.

### 2. Project Structure

Use UV as the package manager. Target Python 3.13+. Organize code into logical modules. Separate concerns: data models, business logic, and CLI interface. Keep the main entry point clean and minimal.

**Rationale**: Clear separation of concerns enables independent testing, reduces coupling, and makes the codebase maintainable as it grows. UV provides fast, reliable dependency management for modern Python projects.

### 3. Development Methodology

Follow spec-driven development principles. Write specifications before implementation. Each feature must be independently testable. Maintain clear boundaries between components.

**Rationale**: Specifying requirements upfront prevents scope creep, ensures alignment on acceptance criteria, and enables parallel work on independent features.

### 4. Data Management

Persist all data in PostgreSQL using well-designed schemas with proper migrations. Use appropriate data structures for efficient operations. Ensure data integrity through constraints, transactions, and ACID compliance. Use unique identifiers for all entities. Implement proper indexing for query performance.

**Rationale**: Persistent, database-backed storage enables multi-user support and data reliability. Well-structured schemas with migrations allow safe evolution of the data model. ACID guarantees ensure correctness in concurrent scenarios.

### 5. User Experience

Provide intuitive web-based UI and clear API responses. Handle errors gracefully with informative messages and user-friendly notifications. Maintain consistent interaction patterns across web interface and API. Support responsive design for desktop and mobile. Design for accessibility.

**Rationale**: A predictable, intuitive experience reduces user frustration. Consistent patterns across UI and API make the application feel professional and maintainable. Real-time feedback keeps users informed.

### 6. API Design

Design RESTful APIs following standard conventions: meaningful resource paths, appropriate HTTP verbs (GET, POST, PUT, DELETE), standard status codes, and descriptive error responses. Version APIs if breaking changes are necessary. Document all endpoints with clear request/response examples.

**Rationale**: Standard conventions make APIs predictable and easier to consume. Clear documentation reduces integration friction. Proper versioning prevents breaking existing clients.

### 7. Code Quality Gates

No global mutable state outside of dependency injection containers. All business logic must be unit testable. Input validation for all user-provided data. Explicit is better than implicit. Use type hints throughout (Python type hints, TypeScript strict mode).

**Rationale**: Eliminating unbounded global state enables isolated testing and reasoning about code behavior. Input validation at system boundaries prevents data corruption. Explicit code is debuggable and maintainable. Type safety prevents entire classes of bugs.

## Constraints

The following constraints are **non-negotiable** and must be respected throughout development:

- **MUST** use PostgreSQL for persistent data storage with proper migrations and schema versioning
- **MUST** expose RESTful APIs that follow standard HTTP conventions (status codes, error handling)
- **MUST** implement proper authentication and authorization (secure password hashing, session management)
- **MUST** integrate with OpenAI Agents SDK for AI-powered features per specification requirements
- **DO NOT** over-engineer solutions; implement only requirements specified in feature specs
- **MUST** handle third-party API failures gracefully without blocking core functionality (task CRUD)
- **ALWAYS** validate user input at system boundaries (API endpoints, form submissions)
- **ALWAYS** provide meaningful error messages and feedback for all operations
- **MUST** use Next.js for frontend with TypeScript; FastAPI with Python for backend
- **MUST** follow principle of least privilege for all permissions and access controls

## Success Criteria

The fullstack application is complete when (MVP baseline):

- Users can register, authenticate, and access their own task dashboard
- Authenticated users can create tasks with title, description, and optional deadline
- Users can view all their tasks organized by status and priority in the web UI
- Users can update and delete their tasks
- Users can mark tasks as complete/incomplete
- PostgreSQL persists all data correctly across sessions
- Backend APIs return appropriate HTTP status codes and error messages
- AI integration generates priority recommendations for new tasks (P1 requirement)
- System gracefully handles OpenAI API failures without breaking task CRUD operations
- All code passes linting, type checking, and security validation
- Unit and integration tests cover core functionality (70%+ coverage)

## Governance

**Amendment Procedure**: Constitution amendments require written justification of the change (rationale, impact on existing code/practices). Changes are documented in a new Prompt History Record with stage `constitution`. Version bumps follow semantic versioning: MAJOR for backward-incompatible principle removals or redefinitions, MINOR for new principles or materially expanded guidance, PATCH for clarifications or non-semantic refinements.

**Compliance Review**: All pull requests and feature implementations must verify alignment with these principles. Violations require documented justification in the commit message or PR description explaining why the constraint is superseded.

**Runtime Guidance**: Developers should consult `CLAUDE.md` in the repository root for implementation-level guidance and tool usage. This constitution defines *what* we build; that file explains *how* we build it.

**Version**: 2.0.0 | **Ratified**: 2025-12-05 | **Last Amended**: 2025-12-08

**Amendment Log**:
- **v2.0.0** (2025-12-08): Major revision to support fullstack architecture
  - Updated Data Management principle to require PostgreSQL persistence
  - Updated UX principle to support web UI instead of CLI-only
  - Added API Design principle (new Principle #6)
  - Replaced legacy constraints (no database) with fullstack requirements (PostgreSQL, APIs, auth, AI)
  - Updated success criteria to reflect fullstack application goals
  - Rationale: Evolution of project scope from Python CLI to fullstack web application with AI features
