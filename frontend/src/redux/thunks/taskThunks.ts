import { createAsyncThunk } from "@reduxjs/toolkit";
import {
  tasksService,
  TaskCreateRequest,
  TaskUpdateRequest,
} from "@/services/tasksService";
import { Task, TaskStatus, TaskPriority } from "@/redux/slices/taskSlice";

/**
 * Async thunk for fetching user tasks with filtering and pagination
 */
export const fetchTasks = createAsyncThunk(
  "tasks/fetchTasks",
  async (
    {
      status,
      priority,
      skip = 0,
      limit = 20,
    }: {
      status?: TaskStatus;
      priority?: TaskPriority;
      skip?: number;
      limit?: number;
    },
    { rejectWithValue }
  ) => {
    try {
      const result = await tasksService.getTasks(
        status,
        priority,
        skip,
        limit
      );
      return result;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to fetch tasks"
      );
    }
  }
);

/**
 * Async thunk for fetching a single task
 */
export const fetchTask = createAsyncThunk(
  "tasks/fetchTask",
  async (taskId: string, { rejectWithValue }) => {
    try {
      const task = await tasksService.getTask(taskId);
      return task;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to fetch task"
      );
    }
  }
);

/**
 * Async thunk for creating a new task
 */
export const createTask = createAsyncThunk(
  "tasks/createTask",
  async (data: TaskCreateRequest, { rejectWithValue }) => {
    try {
      const task = await tasksService.createTask(data);
      return task;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to create task"
      );
    }
  }
);

/**
 * Async thunk for updating a task
 */
export const updateTask = createAsyncThunk(
  "tasks/updateTask",
  async (
    { taskId, data }: { taskId: string; data: TaskUpdateRequest },
    { rejectWithValue }
  ) => {
    try {
      const task = await tasksService.updateTask(taskId, data);
      return task;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to update task"
      );
    }
  }
);

/**
 * Async thunk for deleting a task
 */
export const deleteTask = createAsyncThunk(
  "tasks/deleteTask",
  async (taskId: string, { rejectWithValue }) => {
    try {
      await tasksService.deleteTask(taskId);
      return taskId; // Return ID for removal from state
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to delete task"
      );
    }
  }
);

/**
 * Async thunk for completing/toggling task completion
 */
export const completeTask = createAsyncThunk(
  "tasks/completeTask",
  async (taskId: string, { rejectWithValue }) => {
    try {
      const task = await tasksService.completeTask(taskId);
      return task;
    } catch (error: any) {
      return rejectWithValue(
        error?.response?.data?.error?.message ||
          error?.message ||
          "Failed to complete task"
      );
    }
  }
);
