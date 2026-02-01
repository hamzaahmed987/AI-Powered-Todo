# Redux Persist Token Management - Implementation Guide

## Problem Solved

Fixed the error: **"Cannot read properties of undefined (reading 'access_token')"**

This was caused by:
1. Inconsistent API response handling
2. Redux state not properly persisting tokens
3. Missing error handling for token operations
4. Timing issues with redux-persist rehydration

## Changes Made

### 1. **API Service Updates** (`frontend/src/services/authService.ts`)
- Added proper response structure handling
- Ensured `access_token` is correctly extracted from backend response
- Added fallback handling for different response formats

**Backend Response Format:**
```typescript
// Backend returns AuthToken directly
{
  access_token: string,
  token_type: string,
  expires_in: number
}
```

### 2. **Redux Store Configuration** (`frontend/src/redux/store.ts`)
- Configured separate persist config for auth and tasks
- Only persist essential auth fields: `accessToken`, `user`, `isAuthenticated`
- Prevents unnecessary re-renders from persisting loading/error states

```typescript
const authPersistConfig = {
  key: "auth",
  storage,
  whitelist: ["accessToken", "user", "isAuthenticated"],
};
```

### 3. **Auth Thunks** (`frontend/src/redux/thunks/authThunks.ts`)
- Added validation for token response
- Improved error messages with multiple fallback options
- Stores token in both Redux (via state) AND localStorage (for axios interceptor)

```typescript
// Validates response before storing
if (!result || !result.access_token) {
  return rejectWithValue("Invalid token response from server");
}
```

### 4. **New Custom Hooks**

#### `useToken.ts`
Simple hook to get token from Redux state:
```typescript
export const useToken = () => {
  const accessToken = useAppSelector((state) => state.auth.accessToken);
  return accessToken;
};
```

**Usage:**
```typescript
const token = useToken();
// token is now properly typed and guaranteed from Redux
```

#### `useInitializeAuth.ts`
Ensures auth state is properly synced from localStorage to Redux during rehydration:
```typescript
export const useInitializeAuth = () => {
  const { isInitialized, accessToken, isAuthenticated } = useInitializeAuth();
  // Safe to use auth state immediately
};
```

**Usage in components:**
```typescript
export default function Dashboard() {
  const { isInitialized, accessToken } = useInitializeAuth();

  if (!isInitialized) {
    return <LoadingSpinner />;
  }

  return <YourContent />;
}
```

### 5. **API Client Error Handling**

Updated all API clients (`api.ts`, `services/api.ts`, `agentService.ts`) with:
- Safe localStorage access (wrapped in try-catch)
- Token validation (checks for empty/whitespace tokens)
- Graceful fallback for SSR environments
- Better error messages from backend

```typescript
try {
  const token = localStorage.getItem("accessToken");
  if (token && token.trim()) {
    config.headers.Authorization = `Bearer ${token}`;
  }
} catch (error) {
  console.warn("Could not access localStorage for token");
}
```

## Token Flow Architecture

```
1. User Login
   ↓
2. authService.login() → Backend API
   ↓
3. Backend Returns: { access_token, token_type, expires_in }
   ↓
4. authThunks validates response
   ↓
5. Token stored in:
   - Redux State (via setAccessToken action)
   - localStorage (for axios interceptor)
   ↓
6. redux-persist automatically syncs Redux → localStorage
   ↓
7. On page reload:
   - redux-persist rehydrates from localStorage
   - useInitializeAuth syncs to Redux if needed
   - axios interceptor uses localStorage
   ↓
8. All subsequent API calls include token via Authorization header
```

## Implementation Checklist

- [x] API response handling fixed
- [x] Redux persist configured properly
- [x] Error handling improved
- [x] Token stored in both Redux and localStorage
- [x] useToken hook created
- [x] useInitializeAuth hook created
- [x] axios interceptors updated with error handling
- [x] agentService updated with proper error handling

## Usage in Components

### Example 1: Protected Route/Dashboard
```typescript
"use client";
import { useInitializeAuth } from "@/hooks/useInitializeAuth";
import { useAuth } from "@/hooks/useAuth";

export default function Dashboard() {
  const router = useRouter();
  const { isInitialized, isAuthenticated } = useInitializeAuth();
  const { user } = useAuth();

  useEffect(() => {
    if (isInitialized && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isInitialized, isAuthenticated, router]);

  if (!isInitialized) {
    return null; // or loading spinner
  }

  return (
    <div>
      <h1>Welcome, {user?.email}</h1>
      {/* Your content */}
    </div>
  );
}
```

### Example 2: Getting Token Programmatically
```typescript
"use client";
import { useToken } from "@/hooks/useToken";

export default function MyComponent() {
  const token = useToken();

  const makeCustomRequest = async () => {
    const response = await fetch('/api/custom', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  };

  return <button onClick={makeCustomRequest}>Make Request</button>;
}
```

### Example 3: Login Form
```typescript
"use client";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const router = useRouter();

  const handleLogin = async (email: string, password: string) => {
    try {
      await login({ email, password });
      // Token is now in Redux + localStorage
      router.push("/dashboard");
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  return (
    // Form implementation
  );
}
```

## Debugging Tips

### Check Token in Redux
```typescript
// In browser console
const state = store.getState();
console.log(state.auth.accessToken);
```

### Check localStorage
```typescript
// In browser console
localStorage.getItem('auth')
// or
localStorage.getItem('persist:root')
```

### Verify Redux Persist
```typescript
// Check if persist gate has loaded
// Look for "persist/REHYDRATE" action in Redux DevTools
```

## Environment Configuration

Make sure `.env.local` has correct API URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Common Issues & Solutions

### Issue: Token undefined after login
**Solution:** Use `useInitializeAuth()` hook to ensure rehydration complete

### Issue: 401 errors on API calls
**Solution:** Check that token is properly stored in localStorage
```typescript
console.log(localStorage.getItem('accessToken'));
```

### Issue: Token not persisting after page reload
**Solution:** Ensure redux-persist is configured in store.ts and PersistGate wraps app

### Issue: localStorage not accessible (SSR)
**Solution:** Already handled with try-catch blocks in interceptors

## Testing

### Test Login Flow
1. Clear localStorage: `localStorage.clear()`
2. Clear Redux state (close DevTools)
3. Login with valid credentials
4. Check localStorage for token: `localStorage.getItem('accessToken')`
5. Check Redux: `store.getState().auth.accessToken`
6. Reload page - should remain logged in

### Test API Calls
1. Login successfully
2. Make API call (create task, get tasks, etc)
3. Check Network tab - should have `Authorization: Bearer <token>` header
4. Check response - should be successful (not 401)

## Next Steps

1. Test the login flow end-to-end
2. Verify tokens persist across page reloads
3. Check API calls include proper Authorization header
4. Monitor browser console for any warnings
5. Test logout flow clears token properly

## Files Modified

```
frontend/src/lib/api.ts
frontend/src/services/api.ts
frontend/src/services/authService.ts
frontend/src/services/agentService.ts
frontend/src/redux/store.ts
frontend/src/redux/thunks/authThunks.ts
frontend/src/redux/slices/authSlice.ts (no changes, but relevant)
frontend/src/hooks/useAuth.ts (no changes, but relevant)
```

## Files Created

```
frontend/src/hooks/useToken.ts
frontend/src/hooks/useInitializeAuth.ts
```

---

**Status:** ✅ Complete and Ready for Testing
