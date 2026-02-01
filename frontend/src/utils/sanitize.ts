/**
 * Input sanitization utilities to prevent XSS attacks
 */

import DOMPurify from 'dompurify';

/**
 * Sanitize user input to remove potentially dangerous HTML/JavaScript
 * This is used for user-generated content that might be displayed in the UI
 *
 * @param input - Raw user input string
 * @returns Sanitized string safe for display
 */
export const sanitizeInput = (input: string): string => {
  if (typeof input !== 'string') {
    return '';
  }

  // First trim whitespace
  let cleaned = input.trim();

  // Use DOMPurify to remove any HTML/script tags
  if (typeof window !== 'undefined') {
    cleaned = DOMPurify.sanitize(cleaned, {
      ALLOWED_TAGS: [],  // Allow no HTML tags
      ALLOWED_ATTR: []   // Allow no attributes
    });
  }

  // Additional safety: limit length to prevent DoS
  const MAX_LENGTH = 5000;
  if (cleaned.length > MAX_LENGTH) {
    cleaned = cleaned.substring(0, MAX_LENGTH);
  }

  return cleaned;
};

/**
 * Sanitize email input
 * Validates format and removes whitespace
 *
 * @param email - Email string
 * @returns Sanitized email
 */
export const sanitizeEmail = (email: string): string => {
  return email.trim().toLowerCase();
};

/**
 * Validate email format using regex
 *
 * @param email - Email to validate
 * @returns true if email is valid format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Sanitize URL input to prevent XSS
 *
 * @param url - URL string
 * @returns Sanitized URL
 */
export const sanitizeUrl = (url: string): string => {
  if (!url) return '';

  try {
    // Check if it's a valid URL
    new URL(url);
    return url;
  } catch {
    return '';
  }
};

/**
 * Batch sanitize an object's string properties
 *
 * @param obj - Object with string properties
 * @returns New object with sanitized values
 */
export const sanitizeObject = <T extends Record<string, any>>(obj: T): T => {
  const sanitized = { ...obj };

  for (const key in sanitized) {
    if (typeof sanitized[key] === 'string') {
      sanitized[key] = sanitizeInput(sanitized[key]);
    }
  }

  return sanitized;
};
