/**
 * API Error Types and Response Structures
 */

export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiErrorResponse {
  status: string;
  error: ErrorDetail;
}

export interface AppError {
  status?: number;
  code: string;
  message: string;
  details?: Record<string, any>;
}

/**
 * Error class for application-wide error handling
 */
export class ApiError extends Error {
  status?: number;
  code: string;
  details?: Record<string, any>;

  constructor(code: string, message: string, status?: number, details?: Record<string, any>) {
    super(message);
    this.code = code;
    this.status = status;
    this.details = details;
    this.name = "ApiError";

    // Maintain proper stack trace for where our error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  toJSON(): AppError {
    return {
      status: this.status,
      code: this.code,
      message: this.message,
      details: this.details,
    };
  }
}

/**
 * Error messages for common API errors
 */
export const ERROR_MESSAGES = {
  UNAUTHORIZED: "Your session has expired. Please login again.",
  FORBIDDEN: "You don't have permission to perform this action.",
  NOT_FOUND: "The requested resource was not found.",
  VALIDATION_ERROR: "Please check your input and try again.",
  SERVER_ERROR: "An unexpected error occurred. Please try again later.",
  NETWORK_ERROR: "Network error. Please check your connection.",
  TIMEOUT: "Request timeout. Please try again.",
} as const;

/**
 * Error code constants
 */
export const ERROR_CODES = {
  UNAUTHORIZED: "UNAUTHORIZED",
  FORBIDDEN: "FORBIDDEN",
  NOT_FOUND: "NOT_FOUND",
  VALIDATION_ERROR: "VALIDATION_ERROR",
  SERVER_ERROR: "SERVER_ERROR",
  NETWORK_ERROR: "NETWORK_ERROR",
  TIMEOUT: "TIMEOUT",
  UNKNOWN: "UNKNOWN",
} as const;
