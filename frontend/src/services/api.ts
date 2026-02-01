import axios, { AxiosInstance, AxiosError, AxiosResponse } from "axios";
import { ApiError, ERROR_MESSAGES, ERROR_CODES, ApiErrorResponse } from "@/types/errors";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 second timeout (NeonDB cold start can take time)
});

/**
 * Request interceptor to add auth token from localStorage
 */
api.interceptors.request.use(
  (config) => {
    // Guard against SSR environment
    if (typeof window === "undefined") {
      return config;
    }

    try {
      const token = localStorage.getItem("accessToken");
      if (token && token.trim()) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      // localStorage might have issues
      console.warn("Could not access localStorage for token:", error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(parseError(error));
  }
);

/**
 * Response interceptor to handle errors and auth redirects
 */
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    const parsedError = parseError(error);

    // Handle 401 Unauthorized - redirect to login
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        // Only redirect if not already on auth page
        if (!window.location.pathname.includes("/auth")) {
          localStorage.removeItem("accessToken");
          localStorage.removeItem("user");
          window.location.href = "/auth/login";
        }
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      parsedError.message = ERROR_MESSAGES.FORBIDDEN;
    }

    return Promise.reject(parsedError);
  }
);

/**
 * Parse Axios errors into AppError format
 */
function parseError(error: any): ApiError {
  // Network timeout
  if (error.code === "ECONNABORTED") {
    return new ApiError(
      ERROR_CODES.TIMEOUT,
      ERROR_MESSAGES.TIMEOUT,
      408
    );
  }

  // Network error
  if (!error.response && error.message === "Network Error") {
    return new ApiError(
      ERROR_CODES.NETWORK_ERROR,
      ERROR_MESSAGES.NETWORK_ERROR
    );
  }

  // API Response with error structure
  if (error.response) {
    const data = error.response.data as ApiErrorResponse | any;
    const status = error.response.status;

    // Handle structured error response from backend
    if (data?.error) {
      return new ApiError(
        data.error.code || ERROR_CODES.UNKNOWN,
        data.error.message || getErrorMessageByStatus(status),
        status,
        data.error.details
      );
    }

    // Handle standard error response format
    if (data?.detail) {
      const errorCode = getErrorCodeByStatus(status) || ERROR_CODES.UNKNOWN;
      return new ApiError(
        errorCode,
        typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail),
        status
      );
    }

    // Handle other response formats
    return new ApiError(
      getErrorCodeByStatus(status) || ERROR_CODES.UNKNOWN,
      data?.message || getErrorMessageByStatus(status),
      status
    );
  }

  // Unknown error
  return new ApiError(
    ERROR_CODES.UNKNOWN,
    error?.message || ERROR_MESSAGES.SERVER_ERROR,
    500
  );
}

/**
 * Get error code based on HTTP status code
 */
function getErrorCodeByStatus(status: number): string {
  switch (status) {
    case 400:
      return ERROR_CODES.VALIDATION_ERROR;
    case 401:
      return ERROR_CODES.UNAUTHORIZED;
    case 403:
      return ERROR_CODES.FORBIDDEN;
    case 404:
      return ERROR_CODES.NOT_FOUND;
    case 500:
    case 502:
    case 503:
    case 504:
      return ERROR_CODES.SERVER_ERROR;
    default:
      return ERROR_CODES.UNKNOWN;
  }
}

/**
 * Get error message based on HTTP status code
 */
function getErrorMessageByStatus(status: number): string {
  switch (status) {
    case 400:
      return ERROR_MESSAGES.VALIDATION_ERROR;
    case 401:
      return ERROR_MESSAGES.UNAUTHORIZED;
    case 403:
      return ERROR_MESSAGES.FORBIDDEN;
    case 404:
      return ERROR_MESSAGES.NOT_FOUND;
    case 500:
    case 502:
    case 503:
    case 504:
      return ERROR_MESSAGES.SERVER_ERROR;
    default:
      return ERROR_MESSAGES.SERVER_ERROR;
  }
}

export default api;
