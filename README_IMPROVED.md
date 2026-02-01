# AI-Powered Todo Application

## Overview

This is a full-stack AI-powered todo application featuring advanced task management capabilities with natural language processing and intelligent suggestions. The application combines a FastAPI backend with a Next.js frontend to provide a seamless task management experience enhanced with artificial intelligence.

## Key Features

### AI-Powered Task Management
- Natural language task creation and management
- Intelligent priority suggestions based on task content
- Estimated duration predictions
- Productivity insights and recommendations
- Context-aware task analysis

### Advanced Task Management
- Create, read, update, and delete tasks
- Task status tracking (pending, in-progress, completed)
- Priority levels (low, medium, high, urgent)
- Deadline management
- Estimated duration tracking

### Security & Authentication
- JWT-based authentication
- Secure password hashing
- Role-based access control
- Input validation and sanitization

### Performance & Monitoring
- In-memory caching with TTL
- Structured logging with JSON support
- Request/response time tracking
- Database operation monitoring
- AI interaction logging

## Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT-based with python-jose
- **AI Integration**: OpenAI Agents SDK with OpenRouter compatibility
- **Caching**: Custom in-memory caching
- **Logging**: Structured logging with monitoring

### Frontend (Next.js)
- **Framework**: Next.js 16 with App Router
- **State Management**: Redux Toolkit with RTK Query
- **UI Components**: React with Tailwind CSS
- **API Client**: Axios with interceptors
- **Forms**: Formik with Yup validation

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Authenticate user
- `GET /api/v1/auth/me` - Get current user info

### Task Management
- `GET /api/v1/tasks` - List user tasks with filtering
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### AI Agent
- `POST /api/v1/agent/chat` - Natural language task management
- `GET /api/v1/agent/capabilities` - Get agent capabilities

## Deployment

### Production Deployment
The application is designed for containerized deployment with Docker and supports both Docker Compose and Kubernetes configurations.

#### Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Kubernetes
Apply the provided Kubernetes manifests:
```bash
kubectl apply -f KUBERNETES_DEPLOYMENT.yaml
```

### Environment Configuration
Copy and customize the environment file:
```bash
cp .env.prod.example .env
# Update with your specific values
```

## Security Best Practices

- Use strong, unique passwords for JWT secrets
- Rotate API keys regularly
- Implement HTTPS in production
- Regular security audits
- Input validation and sanitization
- Proper session management

## Performance Optimizations

- Database indexing for common queries
- In-memory caching for frequently accessed data
- Efficient API response structures
- Optimized database queries
- Request/response logging for monitoring

## Development

### Backend Setup
```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests
```bash
cd backend
poetry run pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Monitoring & Logging

The application includes comprehensive logging and monitoring capabilities:
- Structured JSON logs for easy parsing
- Performance metrics tracking
- Database operation monitoring
- AI interaction logging
- Request/response time tracking

## Technologies Used

### Backend
- FastAPI: Modern Python web framework
- SQLAlchemy: Python SQL toolkit and ORM
- PostgreSQL: Relational database
- OpenAI Agents SDK: AI agent framework
- uvicorn: ASGI server

### Frontend
- Next.js: React framework
- React: UI library
- Redux Toolkit: State management
- Tailwind CSS: Utility-first CSS framework
- TypeScript: Type-safe JavaScript

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.