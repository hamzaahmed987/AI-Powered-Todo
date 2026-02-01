import DOMPurify from 'dompurify';

/**
 * Sanitize user input to prevent XSS attacks
 * Removes any HTML/script tags while preserving text
 */
export function sanitizeInput(input: string): string {
  if (!input) return '';

  // Remove HTML tags and trim whitespace
  const cleaned = DOMPurify.sanitize(input, { ALLOWED_TAGS: [] });
  return cleaned.trim();
}

/**
 * Validate task title
 * Must be non-empty and under 200 characters
 */
export function validateTaskTitle(title: string): { valid: boolean; error?: string } {
  const sanitized = sanitizeInput(title);

  if (!sanitized) {
    return { valid: false, error: 'Task title cannot be empty' };
  }

  if (sanitized.length > 200) {
    return { valid: false, error: 'Task title must be under 200 characters' };
  }

  return { valid: true };
}

/**
 * Validate task description
 * Optional field, but if provided must be under 1000 characters
 */
export function validateTaskDescription(description: string): { valid: boolean; error?: string } {
  if (!description) {
    return { valid: true };
  }

  const sanitized = sanitizeInput(description);

  if (sanitized.length > 1000) {
    return { valid: false, error: 'Description must be under 1000 characters' };
  }

  return { valid: true };
}
