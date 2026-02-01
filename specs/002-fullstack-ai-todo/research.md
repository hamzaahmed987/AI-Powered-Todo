# Phase 0 Research: Fullstack AI-Powered Todo App

**Date**: 2025-12-08 | **Feature**: 002-fullstack-ai-todo | **Status**: Complete

## Research Summary

Phase 0 research resolved all architectural unknowns and validated technology choices against best practices. No NEEDS CLARIFICATION items required external research; all decisions derived from spec requirements and modern fullstack development patterns.

---

## Key Decisions

### 1. Authentication & Session Management

**Decision**: JWT-based stateless authentication with secure HTTP-only cookies for tokens

**Rationale**:
- JWT tokens are stateless, reducing server memory overhead for multi-user systems
- HTTP-only cookies prevent XSS token theft while allowing automatic token inclusion in requests
- Aligns with modern SPA (Single Page Application) best practices
- Enables future scaling to multiple backend instances without shared session store

**Alternatives Considered**:
- Session-based (traditional cookies): Requires server-side session store, doesn't scale well
- localStorage for tokens: Vulnerable to XSS attacks, no automatic inclusion in requests
- OAuth2: Over-engineered for single-tenant MVP, adds provider dependency

**Implementation Details**:
- Backend: FastAPI with python-jose for JWT token generation/validation
- Token rotation: Short-lived access tokens (15 mins) with refresh tokens (7 days)
- Password hashing: bcrypt via passlib, never store plain passwords
- Frontend: Store tokens in memory during session, refresh on page reload

---

### 2. Database Schema & Migrations

**Decision**: PostgreSQL with SQLAlchemy ORM and Alembic migrations

**Rationale**:
- PostgreSQL provides ACID guarantees essential for multi-user concurrent access
- SQLAlchemy ORM prevents SQL injection and provides type-safe data access
- Alembic migrations enable safe schema evolution without manual SQL
- Both tools have excellent Python ecosystem integration and documentation

**Alternatives Considered**:
- Raw SQL queries: Error-prone, harder to test, security risks
- NoSQL (MongoDB): Insufficient for complex queries and transactions needed for task prioritization and AI analysis
- SQLite: Single-writer limitation prevents concurrent user access needed for P3 (team features)

**Schema Approach**:
- Separate migrations for each logical data model (users, tasks, sharing)
- Indexes on frequently queried columns (user_id, created_at, status)
- Foreign key constraints for referential integrity
- Timestamps (created_at, updated_at) on all mutable entities

---

### 3. AI Integration Pattern

**Decision**: Service layer wrapper around OpenAI Agents SDK with graceful fallback

**Rationale**:
- Service layer decouples AI logic from API endpoints, enabling independent testing
- Wrapper allows future switching to different AI providers without changing APIs
- Graceful fallback (task CRUD works without AI) meets requirement FR-015

**Alternatives Considered**:
- Direct OpenAI calls in API endpoints: Tightly couples API to OpenAI, harder to test
- Async task queue (Celery): Over-engineered for MVP, adds operational complexity
- Caching AI responses: Adds complexity without clear MVP benefit; can add in optimization phase

**Implementation Details**:
- Dedicated `ai_service.py` with methods: `generate_priority()`, `estimate_duration()`, `suggest_subtasks()`, `analyze_task()`
- Try-catch with timeout handling; returns sensible defaults on OpenAI failure
- Rate limiting via decorator to respect OpenAI API quotas
- Logging all AI API calls for monitoring and billing

---

### 4. Real-Time Task Updates

**Decision**: Polling (first) with WebSocket upgrade path for P2

**Rationale**:
- Polling is simpler for MVP, no additional infrastructure needed
- Suffices for P1 requirements (basic task persistence)
- WebSocket complexity (connection pools, failover) deferred to P2
- Can add subscription-based updates later without breaking existing API

**Alternatives Considered**:
- WebSocket immediately: Requires additional infrastructure, higher operational complexity for MVP
- Server-Sent Events (SSE): Better than polling but requires infrastructure; still less scalable than WebSocket

**Implementation Details** (for MVP):
- Frontend polls `/api/tasks` every 3-5 seconds when dashboard is open
- Last-modified timestamps allow frontend to detect stale data
- Upgrade to WebSocket in P2: Add socket.io or websockets library

---

### 5. Frontend State Management

**Decision**: Zustand for lightweight state management

**Rationale**:
- Minimal boilerplate compared to Redux
- Sufficient for single-tenant MVP with modest feature scope
- Easy to debug (state is just plain objects)
- Small bundle size impact

**Alternatives Considered**:
- Redux: Over-engineered for current scope; Redux Toolkit reduces boilerplate but still verbose
- React Context: Sufficient but requires more manual optimization for performance
- TanStack Query (React Query): Better for server-state, less suitable for client state (auth, UI)

**Implementation Details**:
- Three stores: `authStore` (user, tokens), `taskStore` (tasks list, filters), `uiStore` (modals, toasts)
- Hooks expose store methods as React hooks: `useAuth()`, `useTasks()`, `useUI()`
- Persist auth store to localStorage for session recovery on page reload

---

### 6. Error Handling & API Responses

**Decision**: Standardized error response format with HTTP status codes and error codes

**Rationale**:
- Consistent format makes frontend error handling predictable
- Error codes allow frontend to handle specific errors (e.g., "task_not_found" vs "internal_server_error")
- Aligns with REST best practices

**Standard Response Format**:

Success (200 OK):
```json
{
  "status": "success",
  "data": { /* response payload */ }
}
```

Error (4xx/5xx):
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Task title is required",
    "details": { "field": "title", "reason": "empty" }
  }
}
```

**Error Codes**:
- `AUTH_REQUIRED`: No valid authentication
- `FORBIDDEN`: Authenticated but lacks permission
- `VALIDATION_ERROR`: Invalid request data
- `NOT_FOUND`: Resource doesn't exist
- `CONFLICT`: Operation conflicts with existing state
- `AI_UNAVAILABLE`: OpenAI API failure (non-blocking, task CRUD works)
- `INTERNAL_ERROR`: Server error

---

### 7. API Versioning Strategy

**Decision**: URL path versioning (e.g., `/api/v1/tasks`) with mandatory version in all requests

**Rationale**:
- Explicit versioning in URL is immediately visible and debuggable
- Prevents accidental client requests to different API versions
- Allows running multiple API versions during transition (easier zero-downtime deployments)

**Alternatives Considered**:
- Header-based versioning: Less visible, easier to miss in logs
- No versioning: Breaks backward compatibility without clear migration path

**Implementation Details**:
- All routes under `/api/v1/` namespace from day one
- If breaking changes needed in P2, create `/api/v2/` routes alongside v1
- Deprecation: v1 routes log warnings after v2 launch, sunset in subsequent release

---

## Validation & Trade-offs

### Decisions NOT Made (Deferred to Phase 1 or Later)

1. **WebSocket Implementation**: Deferred to P2; polling suffices for MVP
2. **Search & Filtering**: Not in P1 spec; add indexed queries in Phase 1 design
3. **Email Notifications**: Deferred to P3; no external email service in MVP
4. **Multi-tenancy**: Designed for single-tenant MVP; can add org/workspace support later
5. **Caching Layer (Redis)**: Not needed for MVP; PostgreSQL queries fast enough with proper indexing

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| OpenAI API rate limits | Rate limiter in service layer; queue requests if needed |
| Database connection limits | Connection pooling (SQLAlchemy Pool); monitor in production |
| PostgreSQL downtime | Graceful degradation; show user "maintenance mode" message; don't let UI crash |
| JWT token leaks | HTTP-only cookies + HTTPS only + short expiration + refresh token rotation |
| Concurrent task edits | Optimistic locking via `updated_at` timestamp; frontend detects and alerts user |

---

## Deployment & Environment Assumptions

1. **PostgreSQL**: Cloud-hosted (AWS RDS, Heroku Postgres, Supabase) or self-managed with automated backups
2. **OpenAI API Key**: Securely stored in environment variables, never in code
3. **Frontend Hosting**: Vercel (for Next.js), AWS S3 + CloudFront, or self-hosted
4. **Backend Hosting**: Docker container on AWS ECS, Heroku, Railway, or self-hosted
5. **TLS/HTTPS**: Mandatory in production; generated via Let's Encrypt or cloud provider
6. **Environment Variables**: Use `.env.local` (development) and platform secrets (production)

---

## Summary: Architecture is Validated ✅

All research questions resolved. No blockers for proceeding to Phase 1 (data model, contracts, quickstart).

**Next Steps**:
1. Create `data-model.md` with full database schema
2. Create API contracts in `/contracts/openapi.yaml`
3. Create `quickstart.md` with developer setup instructions
4. Proceed to Phase 2: Task breakdown and implementation planning
