# 📝 AI-Powered Todo Application

A comprehensive full-stack todo application featuring web and mobile interfaces with AI-powered features.

## 🏗️ Architecture Overview

This project follows a **multi-tier architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Mobile App    │    │   Web Frontend   │    │   Backend API    │
│  (React Native) │    │   (Next.js)      │    │   (FastAPI)      │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬────────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────▼─────────────┐
                    │      Database Layer       │
                    │   (PostgreSQL/SQLite)     │
                    └───────────────────────────┘
```

## 📁 Directory Structure

```
├── backend/                 # FastAPI backend application
│   ├── app/                 # Application code
│   │   ├── api/             # API route handlers
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # Business logic
│   │   └── database/        # Database configuration
│   ├── tests/               # Backend tests
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # Next.js web application
│   ├── app/                 # Next.js app router pages
│   ├── components/          # React components
│   ├── lib/                 # Utilities and Redux store
│   └── package.json         # Node.js dependencies
│
├── mobile/                  # React Native mobile application
│   ├── src/                 # Mobile source code
│   └── package.json         # React Native dependencies
│
├── legacy-cli/              # Original CLI application
│   ├── src/                 # CLI source code
│   ├── tests/               # CLI tests
│   └── pyproject.toml       # CLI configuration
│
└── docs/                    # Project documentation
```

## 🚀 Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the backend server:
   ```bash
   python start_server.py
   # Or: uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Mobile Setup

1. Navigate to the mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run on iOS or Android:
   ```bash
   npx react-native run-ios
   npx react-native run-android
   ```

### Legacy CLI Application

The original command-line interface is preserved in the `legacy-cli/` directory for reference:

```bash
cd legacy-cli
python -m venv venv
source venv/bin/activate
pip install -e .
todo  # Run the CLI application
```

## 🌐 API Endpoints

The backend provides a comprehensive REST API:

- `GET /api/tasks` - Retrieve all tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Mark task as complete

API documentation is available at `http://localhost:8000/docs` when the backend is running.

## 🤖 AI Features

The application includes AI-powered features:

- Smart task categorization
- Priority recommendations
- Deadline suggestions
- Natural language processing for task creation

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚢 Deployment

### Backend
- Deploy to cloud platforms (Heroku, Railway, AWS, etc.)
- Configure environment variables
- Set up database connection

### Frontend
- Deploy to Vercel, Netlify, or similar platform
- Configure environment variables for API endpoint
- Set up custom domain if needed

## 📋 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **AI Integration**: OpenAI API
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 14+ with App Router
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS
- **Type Safety**: TypeScript

### Mobile
- **Framework**: React Native
- **State Management**: Redux Toolkit
- **Navigation**: React Navigation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.