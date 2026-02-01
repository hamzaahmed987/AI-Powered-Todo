import { createAsyncThunk } from "@reduxjs/toolkit";
import { authService, LoginRequest, RegisterRequest } from "@/services/authService";
import { User } from "@/redux/slices/authSlice";

interface LoginPayload {
  email: string;
  password: string;
}

interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
}

/**
 * Async thunk for user login
 * Handles JWT token retrieval and stores in localStorage
 */
export const loginUser = createAsyncThunk(
  "auth/loginUser",
  async (credentials: LoginPayload, { rejectWithValue }) => {
    try {
      const result = await authService.login(credentials);

      // Validate response has token
      if (!result || !result.access_token) {
        return rejectWithValue("Invalid token response from server");
      }

      // Store token in localStorage for axios interceptor
      if (typeof window !== "undefined") {
        localStorage.setItem("accessToken", result.access_token);
      }

      return {
        accessToken: result.access_token,
        tokenType: result.token_type,
      };
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.error?.message ||
        error?.message ||
        "Login failed";
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk for user registration
 * Now returns both user and token for auto-login
 */
export const registerUser = createAsyncThunk(
  "auth/registerUser",
  async (data: RegisterPayload, { rejectWithValue }) => {
    try {
      const result = await authService.register(data);

      // Validate response has token and user
      if (!result || !result.access_token || !result.user) {
        return rejectWithValue("Invalid registration response from server");
      }

      // Store in localStorage for axios interceptor
      if (typeof window !== "undefined") {
        localStorage.setItem("accessToken", result.access_token);
        localStorage.setItem("user", JSON.stringify(result.user));
      }

      return {
        user: result.user,
        accessToken: result.access_token,
        tokenType: result.token_type,
      };
    } catch (error: any) {
      const errorMessage =
        error?.response?.data?.detail ||
        error?.response?.data?.error?.message ||
        error?.message ||
        "Registration failed";
      return rejectWithValue(errorMessage);
    }
  }
);

/**
 * Async thunk for user logout
 */
export const logoutUser = createAsyncThunk(
  "auth/logoutUser",
  async (_, { rejectWithValue }) => {
    try {
      authService.logout();
      return null;
    } catch (error: any) {
      return rejectWithValue("Logout failed");
    }
  }
);
