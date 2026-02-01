# React Native Mobile App Setup Guide

This guide explains how to connect your React Native mobile app to this FastAPI backend deployed on Vercel.

## 🚀 Quick Start

### Backend Configuration (Already Done ✓)

The backend is configured to work with React Native mobile apps:

1. ✅ **CORS enabled for all origins** (`ALLOWED_ORIGINS=*`)
2. ✅ **JWT authentication** via `Authorization: Bearer <token>` header
3. ✅ **Mobile-friendly response headers** with explicit Content-Type
4. ✅ **OPTIONS preflight handling** for CORS requests
5. ✅ **Health check endpoint** at `/health`

### React Native Client Setup

#### 1. Install Dependencies

```bash
npm install axios
# or
yarn add axios
```

#### 2. Configure API Base URL

Create an API configuration file:

```javascript
// src/config/api.js
const API_BASE_URL = __DEV__
  ? 'http://localhost:8000'  // Development (local backend)
  : 'https://your-app.vercel.app';  // Production (Vercel deployment)

export default API_BASE_URL;
```

#### 3. Create API Client

```javascript
// src/services/api.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import API_BASE_URL from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - redirect to login
      await AsyncStorage.removeItem('access_token');
      // Navigate to login screen
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### 4. Example: Authentication

```javascript
// src/services/auth.js
import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const register = async (email, password, fullName) => {
  try {
    const response = await api.post('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    });

    // Save token
    await AsyncStorage.setItem('access_token', response.data.access_token);

    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const login = async (email, password) => {
  try {
    const response = await api.post('/api/v1/auth/login', {
      email,
      password,
    });

    // Save token
    await AsyncStorage.setItem('access_token', response.data.access_token);

    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await api.post('/api/v1/auth/logout');
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};
```

#### 5. Example: Task Management

```javascript
// src/services/tasks.js
import api from './api';

export const getTasks = async (status = null, priority = null) => {
  try {
    const params = {};
    if (status) params.status = status;
    if (priority) params.priority = priority;

    const response = await api.get('/api/v1/tasks', { params });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const createTask = async (title, description, deadline) => {
  try {
    const response = await api.post('/api/v1/tasks', {
      title,
      description,
      deadline,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const updateTask = async (taskId, updates) => {
  try {
    const response = await api.put(`/api/v1/tasks/${taskId}`, updates);
    return response.data;
  } catch (error) {
    throw error.response?.data || error;
  }
};

export const deleteTask = async (taskId) => {
  try {
    await api.delete(`/api/v1/tasks/${taskId}`);
  } catch (error) {
    throw error.response?.data || error;
  }
};
```

#### 6. Health Check

```javascript
// Check backend connectivity
import api from './services/api';

const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    console.log('Backend status:', response.data.status);
    return response.data;
  } catch (error) {
    console.error('Backend unavailable:', error);
    throw error;
  }
};
```

## 🔐 Authentication Flow

1. **Register/Login** → Receive JWT token
2. **Store token** → AsyncStorage
3. **Add token to requests** → `Authorization: Bearer <token>`
4. **Handle 401 errors** → Clear token and redirect to login

## 📱 Platform-Specific Notes

### iOS

For local development, update `ios/Info.plist` to allow HTTP:

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <true/>
</dict>
```

### Android

For local development, use your computer's IP instead of `localhost`:

```javascript
const API_BASE_URL = __DEV__
  ? 'http://192.168.1.100:8000'  // Replace with your IP
  : 'https://your-app.vercel.app';
```

## 🌐 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/check-email?email=xxx` - Check email availability

### Tasks
- `GET /api/v1/tasks` - List tasks (with filters)
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks/{id}` - Get task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task

### AI Agent
- `POST /api/v1/agent/chat` - Chat with AI task agent

### Health
- `GET /health` - Check backend health

## 🐛 Troubleshooting

### CORS Errors

**Problem**: "Network request failed" or CORS errors

**Solution**: The backend is configured with `ALLOWED_ORIGINS=*`. Ensure:
1. Vercel environment variable `ALLOWED_ORIGINS` is set to `*`
2. Backend is deployed and running
3. Using correct API URL

### Authentication Errors

**Problem**: 401 Unauthorized

**Solution**:
1. Check token is stored: `await AsyncStorage.getItem('access_token')`
2. Verify token format: `Authorization: Bearer <token>`
3. Token may be expired (24h expiration) - re-login

### Network Timeouts

**Problem**: Request timeout

**Solution**:
1. Increase timeout: `axios.create({ timeout: 30000 })`
2. Check backend health: `GET /health`
3. Verify internet connection

### Local Development Issues

**Problem**: Cannot connect to localhost

**Solution**:
- **iOS Simulator**: Use `http://localhost:8000`
- **Android Emulator**: Use `http://10.0.2.2:8000`
- **Physical Device**: Use your computer's IP (e.g., `http://192.168.1.100:8000`)

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Native Networking](https://reactnative.dev/docs/network)
- [Axios Documentation](https://axios-http.com/)
- [AsyncStorage](https://react-native-async-storage.github.io/async-storage/)

## 🆘 Support

For issues or questions:
1. Check `/health` endpoint for backend status
2. Review backend logs in Vercel dashboard
3. Verify environment variables in Vercel
4. Test API endpoints in Postman/Insomnia first

---

**Your Vercel Backend URL**: `https://your-app-name.vercel.app`

Replace this with your actual Vercel deployment URL in your React Native app configuration.
