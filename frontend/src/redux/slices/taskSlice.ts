import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import {
  fetchTasks,
  fetchTask,
  createTask,
  updateTask as updateTaskThunk,
  deleteTask as deleteTaskThunk,
  completeTask,
} from "@/redux/thunks/taskThunks";

export type TaskStatus = "pending" | "in_progress" | "completed";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

export interface Task {
  id: string;
  owner_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority?: TaskPriority;
  ai_priority?: TaskPriority;
  deadline?: string;
  estimated_duration?: number;
  ai_estimated_duration?: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
}

interface TaskState {
  tasks: Task[];
  filters: TaskFilters;
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  skip: number;
  limit: number;
}

const initialState: TaskState = {
  tasks: [],
  filters: {},
  isLoading: false,
  error: null,
  totalCount: 0,
  skip: 0,
  limit: 20,
};

const taskSlice = createSlice({
  name: "tasks",
  initialState,
  reducers: {
    setTasks: (state, action: PayloadAction<Task[]>) => {
      state.tasks = action.payload;
    },
    setFilters: (state, action: PayloadAction<TaskFilters>) => {
      state.filters = action.payload;
      state.skip = 0;
    },
    setIsLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setPagination: (state, action: PayloadAction<{ skip: number; limit: number; totalCount: number }>) => {
      state.skip = action.payload.skip;
      state.limit = action.payload.limit;
      state.totalCount = action.payload.totalCount;
    },
    clearTasks: (state) => {
      state.tasks = [];
      state.filters = {};
      state.isLoading = false;
      state.error = null;
      state.totalCount = 0;
      state.skip = 0;
    },
    addTask: (state, action: PayloadAction<Task>) => {
      state.tasks.unshift(action.payload);
    },
    updateTask: (state, action: PayloadAction<Task>) => {
      const index = state.tasks.findIndex((t) => t.id === action.payload.id);
      if (index !== -1) {
        state.tasks[index] = action.payload;
      }
    },
    deleteTask: (state, action: PayloadAction<string>) => {
      state.tasks = state.tasks.filter((t) => t.id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    // Fetch Tasks
    builder
      .addCase(fetchTasks.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.isLoading = false;
        state.tasks = action.payload.tasks;
        state.totalCount = action.payload.total;
        state.skip = action.payload.skip;
        state.limit = action.payload.limit;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch Single Task
    builder
      .addCase(fetchTask.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchTask.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.tasks.findIndex(
          (t) => t.id === action.payload.id
        );
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
      })
      .addCase(fetchTask.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create Task
    builder
      .addCase(createTask.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.isLoading = false;
        state.tasks.unshift(action.payload);
      })
      .addCase(createTask.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update Task
    builder
      .addCase(updateTaskThunk.pending, (state) => {
        state.error = null;
      })
      .addCase(updateTaskThunk.fulfilled, (state, action) => {
        const index = state.tasks.findIndex(
          (t) => t.id === action.payload.id
        );
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
      })
      .addCase(updateTaskThunk.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Delete Task
    builder
      .addCase(deleteTaskThunk.pending, (state) => {
        state.error = null;
      })
      .addCase(deleteTaskThunk.fulfilled, (state, action) => {
        state.tasks = state.tasks.filter((t) => t.id !== action.payload);
      })
      .addCase(deleteTaskThunk.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Complete Task
    builder
      .addCase(completeTask.pending, (state) => {
        state.error = null;
      })
      .addCase(completeTask.fulfilled, (state, action) => {
        const index = state.tasks.findIndex(
          (t) => t.id === action.payload.id
        );
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
      })
      .addCase(completeTask.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const {
  setTasks,
  setFilters,
  setIsLoading,
  setError,
  clearError,
  setPagination,
  clearTasks,
  addTask,
  updateTask,
  deleteTask,
} = taskSlice.actions;

export default taskSlice.reducer;
