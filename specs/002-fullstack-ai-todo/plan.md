# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the existing Python CLI todo app into a fullstack web application with AI-powered features. Implement a Next.js frontend with TypeScript for responsive, modern UX; FastAPI backend with Python for REST APIs and OpenAI Agents SDK integration; and PostgreSQL for persistent multi-user data storage. Enable users to create tasks, receive AI-generated insights (priority recommendations, duration estimates, subtask suggestions), and collaborate with team members in real-time.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.0+ (Next.js 14+)

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy ORM, Pydantic, OpenAI Agents SDK, python-jose (JWT), psycopg2
- Frontend: Next.js, React 18+, TypeScript, TailwindCSS, axios, zustand (state management)

**Storage**: PostgreSQL 14+ with proper migrations and schema versioning

**Testing**:
- Backend: pytest with pytest-asyncio, httpx for API testing
- Frontend: Jest, React Testing Library

**Target Platform**: Linux/Unix servers (production), Windows/macOS for development

**Project Type**: Web application (fullstack: backend API + frontend SPA)

**Performance Goals**:
- API response time: <200ms p95 for task operations, <3s for AI features
- Frontend load time: <2s for dashboard with 100+ tasks
- Database query time: <100ms for indexed queries
- AI feature latency: <3s for priority/duration recommendations (not blocking UI)

**Constraints**:
- Must handle graceful degradation when OpenAI API is unavailable
- PostgreSQL must support concurrent access with proper connection pooling
- Authentication must use secure session management (JWT or session cookies)
- Frontend must be responsive for mobile (CSS media queries, mobile-first design)

**Scale/Scope**:
- Initial: Single-tenant MVP for 1-100 users with <500 tasks per user
- Future scaling: Multi-tenant, 10k+ concurrent users
- Codebase: ~3-5k LOC for MVP (backend + frontend)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution v2.0.0 (Updated 2025-12-08) - FULLY COMPLIANT** ✅

1. **Clean Code Standards**: ✅ Backend uses FastAPI with Pydantic for type-safe validation; Frontend uses TypeScript strict mode. All modules have clear separation of concerns.
2. **Project Structure**: ✅ Separate backend and frontend directories; organized by feature (models, services, components); migrations for schema evolution.
3. **Development Methodology**: ✅ Spec-driven development being followed; feature spec completed; architecture plan in progress; each user story independently testable.
4. **Data Management**: ✅ PostgreSQL for persistent storage with migrations; ACID compliance; proper indexing; constraints at database level.
5. **User Experience**: ✅ Responsive web UI with Next.js; RESTful APIs with clear error messages; real-time task updates; graceful handling of AI API failures.
6. **API Design**: ✅ RESTful conventions; standard HTTP methods and status codes; documented endpoints; error response format defined.
7. **Code Quality Gates**: ✅ Dependency injection for backends; business logic testable; input validation at API boundaries; type hints throughout.

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-ai-todo/
├── spec.md              # Feature specification (COMPLETED)
├── plan.md              # This file - Implementation plan (THIS PHASE)
├── research.md          # Phase 0 output - Research findings (IN PROGRESS)
├── data-model.md        # Phase 1 output - Database schema (PENDING)
├── quickstart.md        # Phase 1 output - Developer setup (PENDING)
├── contracts/           # Phase 1 output - API contracts (PENDING)
│   ├── openapi.yaml     # OpenAPI 3.0 spec for REST APIs
│   └── error-responses.md # Standard error response format
├── checklists/
│   └── requirements.md   # Quality validation (COMPLETED)
└── tasks.md             # Phase 2 output - Task breakdown (PENDING)
```

### Source Code (fullstack structure)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                          # FastAPI app initialization
│   ├── config.py                        # Configuration, environment variables
│   ├── dependencies.py                  # Dependency injection
│   ├── models/                          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py                      # User model
│   │   ├── task.py                      # Task model
│   │   ├── task_share.py                # TaskShare for collaboration
│   │   ├── task_comment.py              # TaskComment (P3)
│   │   └── audit_log.py                 # AuditLog for monitoring
│   ├── schemas/                         # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   └── shared.py                    # Common schemas
│   ├── api/                             # API routes
│   │   ├── __init__.py
│   │   ├── auth.py                      # Authentication endpoints (register, login, logout)
│   │   ├── tasks.py                     # Task CRUD endpoints
│   │   ├── ai.py                        # AI insights endpoints
│   │   └── shared_tasks.py              # Sharing endpoints (P3)
│   ├── services/                        # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── task_service.py
│   │   ├── ai_service.py                # OpenAI Agents SDK integration
│   │   └── auth_service.py              # Password hashing, token generation
│   ├── database/
│   │   ├── __init__.py
│   │   ├── session.py                   # Database session management
│   │   └── migrations/                  # Alembic migrations
│   │       └── versions/
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── exceptions.py                # Custom exception classes
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_schemas.py
│   ├── integration/
│   │   ├── test_auth_api.py
│   │   ├── test_task_api.py
│   │   └── test_ai_api.py
│   └── conftest.py                      # Pytest fixtures
├── pyproject.toml                       # Python dependencies
├── requirements.txt                     # Pinned dependencies
└── README.md

frontend/
├── src/
│   ├── app/                             # Next.js app directory
│   │   ├── layout.tsx                   # Root layout with auth provider
│   │   ├── page.tsx                     # Home/login page
│   │   ├── dashboard/                   # Main dashboard
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── components/
│   │   │       ├── TaskList.tsx
│   │   │       ├── TaskForm.tsx
│   │   │       ├── TaskItem.tsx
│   │   │       └── AIInsights.tsx
│   │   ├── api/                         # API routes (if needed for middleware)
│   │   └── auth/
│   │       ├── register/
│   │       │   └── page.tsx
│   │       └── login/
│   │           └── page.tsx
│   ├── components/                      # Reusable components
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Toast.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Navigation.tsx
│   │   └── features/
│   │       ├── TaskActions.tsx
│   │       └── ShareTask.tsx             # (P3)
│   ├── services/
│   │   ├── api.ts                       # Axios instance, API calls
│   │   ├── auth.ts                      # Authentication helpers
│   │   └── tasks.ts                     # Task API calls
│   ├── store/                           # Zustand state management
│   │   ├── authStore.ts
│   │   ├── taskStore.ts
│   │   └── uiStore.ts
│   ├── hooks/                           # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useTasks.ts
│   │   └── useApi.ts
│   ├── types/                           # TypeScript types
│   │   ├── index.ts
│   │   ├── api.ts
│   │   └── domain.ts
│   ├── styles/
│   │   └── globals.css                  # TailwindCSS imports
│   └── middleware.ts                    # Next.js middleware (auth checks)
├── tests/
│   ├── unit/
│   │   ├── components/
│   │   └── services/
│   ├── integration/
│   │   └── pages/
│   └── __mocks__/
├── jest.config.js
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
├── package.json
├── .env.example
└── README.md

docker-compose.yml                       # Local development environment
.env.example                             # Environment template (root)
```

**Structure Decision**: Monorepo with separate `backend/` and `frontend/` directories enables independent development, testing, and deployment while sharing a single git history. This supports parallel work and clear responsibility boundaries.

## Complexity Tracking

**N/A** - Constitution Check fully passed. No violations to justify. Architecture decisions are straightforward:

1. **Monorepo** (not multiple repos): Enables unified versioning, shared documentation, single source of truth
2. **FastAPI + SQLAlchemy**: Industry-standard async-capable web framework with mature ORM for Python
3. **Next.js + TypeScript**: Modern React framework with excellent developer experience, built-in routing, and type safety
4. **PostgreSQL**: Battle-tested relational database with excellent Python support, migrations, and multi-user concurrency
5. **Zustand for state**: Lightweight alternative to Redux, sufficient for single-tenant MVP without over-engineering
