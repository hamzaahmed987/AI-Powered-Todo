import api from "./api";
import { Task, TaskStatus, TaskPriority } from "@/redux/slices/taskSlice";

export interface TaskCreateRequest {
  title: string;
  description?: string;
  deadline?: string;
  priority?: TaskPriority;
  estimated_duration?: number;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  deadline?: string;
  estimated_duration?: number;
}

export interface PaginatedTasksResponse {
  status: string;
  data: {
    items: Task[];
    total: number;
    skip: number;
    limit: number;
  };
}

export interface TaskResponse {
  status: string;
  data: Task;
}

/**
 * Type for raw task data from API
 */
interface RawTask {
  id?: string | number;
  owner_id?: string | number;
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  deadline?: string | null;
  estimated_duration?: number | null;
  ai_estimated_duration?: number | null;
  ai_priority?: TaskPriority | null;
  created_at?: string | null;
  updated_at?: string | null;
  completed_at?: string | null;
}

/**
 * Normalize task response from backend
 * Converts any timestamp strings to ISO format
 */
function normalizeTask(task: RawTask): Task {
  return {
    id: typeof task.id === 'string' ? task.id : String(task.id || ''),
    owner_id: typeof task.owner_id === 'string' ? task.owner_id : String(task.owner_id || ''),
    title: task.title || '',
    description: task.description || undefined,
    status: task.status || 'pending',
    priority: task.priority || 'medium',
    deadline: task.deadline ? new Date(task.deadline).toISOString() : undefined,
    estimated_duration: task.estimated_duration || undefined,
    ai_estimated_duration: task.ai_estimated_duration || undefined,
    ai_priority: task.ai_priority || undefined,
    created_at: task.created_at ? new Date(task.created_at).toISOString() : new Date().toISOString(),
    updated_at: task.updated_at ? new Date(task.updated_at).toISOString() : new Date().toISOString(),
    completed_at: task.completed_at ? new Date(task.completed_at).toISOString() : undefined,
  };
}

// Define response types
interface ApiResponse<T> {
  data: T;
}

interface TaskApiResponse {
  status: string;
  data: Task;
}

interface TasksApiResponse {
  status: string;
  data: {
    items: Task[];
    total: number;
    skip: number;
    limit: number;
  };
}

export const tasksService = {
  getTasks: async (
    status?: TaskStatus,
    priority?: TaskPriority,
    skip: number = 0,
    limit: number = 20
  ): Promise<{ tasks: Task[]; total: number; skip: number; limit: number }> => {
    const params: Record<string, string | number | undefined> = { skip, limit };
    if (status) params.status = status;
    if (priority) params.priority = priority;

    try {
      const response = await api.get<ApiResponse<TasksApiResponse> | Task[] | TasksApiResponse>("tasks", { params });

      // Handle different response formats from backend
      let items: Task[] = [];
      let total = 0;

      if ('data' in response.data) {
        // Handle response format: { data: { items: [...], total: N, skip: N, limit: N } }
        if ('items' in response.data.data) {
          items = response.data.data.items.map(normalizeTask);
          total = response.data.data.total;
        }
        // Handle response format: { data: Task[] }
        else if (Array.isArray(response.data.data)) {
          items = response.data.data.map(normalizeTask);
          total = response.data.data.length;
        }
      }
      // Handle response format: Task[]
      else if (Array.isArray(response.data)) {
        items = response.data.map(normalizeTask);
        total = response.data.length;
      }

      return {
        tasks: items,
        total,
        skip: skip || 0,
        limit: limit || 20,
      };
    } catch (error) {
      console.error("Error fetching tasks:", error);
      throw error;
    }
  },

  getTask: async (taskId: string): Promise<Task> => {
    try {
      const response = await api.get<ApiResponse<TaskApiResponse> | Task>(`tasks/${taskId}`);
      // Handle different response formats
      const task = 'data' in response.data ? response.data.data : response.data;
      return normalizeTask(task);
    } catch (error) {
      console.error(`Error fetching task ${taskId}:`, error);
      throw error;
    }
  },

  createTask: async (data: TaskCreateRequest): Promise<Task> => {
    try {
      const response = await api.post<ApiResponse<TaskApiResponse> | Task>("tasks", data);
      // Handle different response formats
      const task = 'data' in response.data ? response.data.data : response.data;
      return normalizeTask(task);
    } catch (error) {
      console.error("Error creating task:", error);
      throw error;
    }
  },

  updateTask: async (
    taskId: string,
    data: TaskUpdateRequest
  ): Promise<Task> => {
    try {
      const response = await api.put<ApiResponse<TaskApiResponse> | Task>(`tasks/${taskId}`, data);
      // Handle different response formats
      const task = 'data' in response.data ? response.data.data : response.data;
      return normalizeTask(task);
    } catch (error) {
      console.error(`Error updating task ${taskId}:`, error);
      throw error;
    }
  },

  deleteTask: async (taskId: string): Promise<void> => {
    try {
      await api.delete(`tasks/${taskId}`);
    } catch (error) {
      console.error(`Error deleting task ${taskId}:`, error);
      throw error;
    }
  },

  completeTask: async (taskId: string): Promise<Task> => {
    // Note: Backend may not have a /complete endpoint, use updateTask instead
    try {
      const response = await api.patch<ApiResponse<TaskApiResponse> | Task>(
        `tasks/${taskId}/complete`
      );
      const task = 'data' in response.data ? response.data.data : response.data;
      return normalizeTask(task);
    } catch (error) {
      console.error(`Error completing task ${taskId} via patch:`, error);
      // Fallback: use updateTask with status=completed
      try {
        return await tasksService.updateTask(taskId, { status: 'completed' });
      } catch (updateError) {
        console.error(`Fallback update also failed for task ${taskId}:`, updateError);
        throw updateError;
      }
    }
  },
};
