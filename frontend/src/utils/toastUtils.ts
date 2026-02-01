import { toast } from "react-toastify";

export const showToast = {
  // Auth toasts
  loginSuccess: () => toast.success("✅ Login successful! Welcome back!"),
  loginError: (message?: string) => toast.error(`❌ Login failed: ${message || "Please try again"}`),
  registerSuccess: () => toast.success("✅ Account created! Logging you in..."),
  registerError: (message?: string) => toast.error(`❌ Registration failed: ${message || "Please try again"}`),
  logoutSuccess: () => toast.success("✅ Logged out successfully!"),

  // Task toasts
  taskCreated: (taskTitle: string) => toast.success(`✅ Task "${taskTitle}" created!`),
  taskCreatedError: (message?: string) => toast.error(`❌ Failed to create task: ${message || "Please try again"}`),

  taskUpdated: (taskTitle: string) => toast.success(`✅ Task "${taskTitle}" updated!`),
  taskUpdatedError: (message?: string) => toast.error(`❌ Failed to update task: ${message || "Please try again"}`),

  taskDeleted: (taskTitle: string) => toast.success(`✅ Task "${taskTitle}" deleted!`),
  taskDeletedError: (message?: string) => toast.error(`❌ Failed to delete task: ${message || "Please try again"}`),

  taskCompleted: (taskTitle: string) => toast.success(`✅ Task "${taskTitle}" marked complete!`),
  taskCompletedError: (message?: string) => toast.error(`❌ Failed to complete task: ${message || "Please try again"}`),

  // Chat toasts
  chatSuccess: (action: string) => toast.success(`✅ ${action} completed!`),
  chatError: (message?: string) => toast.error(`❌ Chat error: ${message || "Please try again"}`),

  // Generic toasts
  success: (message: string) => toast.success(`✅ ${message}`),
  error: (message: string) => toast.error(`❌ ${message}`),
  info: (message: string) => toast.info(`ℹ️ ${message}`),
  loading: (message: string) => toast.loading(`⏳ ${message}`),
};
