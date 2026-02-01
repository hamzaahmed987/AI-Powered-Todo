# Todo App Backend

FastAPI-based REST API backend for the AI-powered Todo application.

## Features

- User registration and authentication with JWT
- Task CRUD operations with PostgreSQL persistence
- AI-powered task analysis and suggestions using OpenAI Agents SDK
- Role-based access control for task sharing
- Real-time task updates with polling support
- Comprehensive error handling and logging

## Tech Stack

- **Framework**: FastAPI 0.104
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **Authentication**: JWT with python-jose
- **Password Security**: bcrypt via passlib
- **AI Integration**: OpenAI SDK
- **Testing**: pytest with pytest-asyncio
- **Code Quality**: black, ruff, mypy

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration and settings
│   ├── dependencies.py         # Dependency injection
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic validation schemas
│   ├── api/                    # API route handlers
│   ├── services/               # Business logic layer
│   ├── database/               # Database session and migrations
│   └── utils/                  # Utilities and helpers
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Pytest fixtures
├── pyproject.toml              # Project metadata and dependencies
├── requirements.txt            # Pinned dependencies
└── README.md                   # This file
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip or uv package manager

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # Or with uv:
   uv sync
   ```

4. **Setup environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your database URL and OpenAI API key
   nano .env.local
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

Server will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI spec**: `http://localhost:8000/openapi.json`

## Database

### Migrations

Migrations are handled with Alembic:

```bash
# Apply all pending migrations
alembic upgrade head

# Create new migration (after model changes)
alembic revision --autogenerate -m "Add status field to tasks"

# Revert last migration
alembic downgrade -1

# View current revision
alembic current
```

### Connection Pool

SQLAlchemy is configured with connection pooling:
- Pool size: 10
- Max overflow: 20
- Recycle: 3600 seconds

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_models.py

# Run tests matching pattern
pytest -k "test_create_task"

# Watch mode
pytest-watch
```

## Code Quality

```bash
# Format code with black
black app/ tests/

# Lint with ruff
ruff check app/ tests/

# Type checking with mypy
mypy app/

# All checks
black --check app/ tests/ && ruff check app/ tests/ && mypy app/
```

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- **DATABASE_URL**: PostgreSQL connection string
- **OPENAI_API_KEY**: OpenAI API key for AI features
- **JWT_SECRET_KEY**: Secret key for JWT token generation
- **ALLOWED_ORIGINS**: CORS allowed origins (comma-separated)
- **DEBUG**: Debug mode (true/false)
- **PORT**: Server port (default: 8000)

## AI Integration

The application uses OpenAI Agents SDK for AI-powered features:

- Task priority generation
- Task duration estimation
- Subtask suggestions
- Natural language task analysis

See `app/docs/ai_integration.md` for detailed integration documentation.

## Deployment

See `../../docs/DEPLOYMENT.md` for production deployment instructions.

## Contributing

1. Create feature branch from `002-fullstack-ai-todo`
2. Follow code style guidelines (see "Code Quality" section)
3. Write tests for new features
4. Run full test suite before submitting PR
5. Update documentation if needed

## License

MIT

## Support

For issues and questions, see the main project documentation in `/specs/002-fullstack-ai-todo/`
