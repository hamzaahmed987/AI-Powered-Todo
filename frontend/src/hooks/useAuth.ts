import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { clearAuth } from "@/redux/slices/authSlice";
import {
  loginUser,
  registerUser,
  logoutUser,
} from "@/redux/thunks/authThunks";
import type { LoginRequest, RegisterRequest } from "@/services/authService";

// Minimal version for testing
export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, accessToken, isAuthenticated, isLoading, error } =
    useAppSelector((state) => state.auth);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      const result = await dispatch(
        loginUser(credentials as { email: string; password: string })
      );
      if (loginUser.fulfilled.match(result)) {
        return result.payload;
      }

      // Handle different types of error payloads
      let errorMessage = 'Login failed';
      if (result.payload instanceof Error) {
        errorMessage = result.payload.message;
      } else if (typeof result.payload === 'string') {
        errorMessage = result.payload;
      } else if (result.payload && typeof result.payload === 'object') {
        errorMessage = (result.payload as { message?: string }).message || JSON.stringify(result.payload);
      } else if (result.error?.message) {
        errorMessage = result.error.message;
      }

      // Provide user-friendly messages for common authentication errors
      if (errorMessage.toLowerCase().includes('email not found')) {
        errorMessage = 'Email not found. Please check your email or sign up.';
      } else if (errorMessage.toLowerCase().includes('invalid credentials')) {
        errorMessage = 'Invalid credentials. Please check your email and password.';
      } else if (errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }

      throw new Error(errorMessage);
    },
    [dispatch]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const result = await dispatch(registerUser(data));
      if (registerUser.fulfilled.match(result)) {
        return result.payload;
      }

      // Handle different types of error payloads
      let errorMessage = 'Registration failed';
      if (result.payload instanceof Error) {
        errorMessage = result.payload.message;
      } else if (typeof result.payload === 'string') {
        errorMessage = result.payload;
      } else if (result.payload && typeof result.payload === 'object') {
        errorMessage = (result.payload as { message?: string }).message || JSON.stringify(result.payload);
      } else if (result.error?.message) {
        errorMessage = result.error.message;
      }

      // Provide user-friendly messages for common authentication errors
      if (errorMessage.toLowerCase().includes('email') && errorMessage.toLowerCase().includes('exists')) {
        errorMessage = 'An account with this email already exists. Please use a different email or try logging in.';
      } else if (errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('fetch')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      }

      throw new Error(errorMessage);
    },
    [dispatch]
  );

  const logout = useCallback(() => {
    dispatch(logoutUser()).then(() => {
      dispatch(clearAuth());
    });
  }, [dispatch]);

  return {
    user,
    accessToken,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
  };
};
