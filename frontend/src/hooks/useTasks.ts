import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import {
  setTasks,
  addTask,
  updateTask,
  deleteTask,
  setFilters,
  setIsLoading,
  setError,
  setPagination,
  clearTasks,
} from "@/redux/slices/taskSlice";
import { tasksService, TaskCreateRequest, TaskUpdateRequest } from "@/services/tasksService";
import { Task, TaskStatus, TaskPriority } from "@/redux/slices/taskSlice";

export const useTasks = () => {
  const dispatch = useAppDispatch();
  const { tasks, filters, isLoading, error, totalCount, skip, limit } =
    useAppSelector((state) => state.tasks);

  const fetchTasks = useCallback(
    async (
      status?: TaskStatus,
      priority?: TaskPriority,
      pageSkip: number = 0,
      pageLimit: number = 20
    ) => {
      dispatch(setIsLoading(true));
      dispatch(setError(null));

      try {
        const response = await tasksService.getTasks(
          status,
          priority,
          pageSkip,
          pageLimit
        );

        dispatch(setTasks(response.tasks));
        dispatch(
          setPagination({
            skip: response.skip,
            limit: response.limit,
            totalCount: response.total,
          })
        );

        dispatch(setIsLoading(false));
        return response;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to fetch tasks";
        dispatch(setError(errorMessage));
        dispatch(setIsLoading(false));
        throw err;
      }
    },
    [dispatch]
  );

  const getTask = useCallback(
    async (taskId: string) => {
      dispatch(setIsLoading(true));
      dispatch(setError(null));

      try {
        const task = await tasksService.getTask(taskId);
        dispatch(setIsLoading(false));
        return task;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to fetch task";
        dispatch(setError(errorMessage));
        dispatch(setIsLoading(false));
        throw err;
      }
    },
    [dispatch]
  );

  const createTask = useCallback(
    async (data: TaskCreateRequest) => {
      dispatch(setError(null));

      try {
        const task = await tasksService.createTask(data);
        dispatch(addTask(task));
        return task;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to create task";
        dispatch(setError(errorMessage));
        throw err;
      }
    },
    [dispatch]
  );

  const updateTaskItem = useCallback(
    async (taskId: string, data: TaskUpdateRequest) => {
      dispatch(setError(null));

      try {
        const task = await tasksService.updateTask(taskId, data);
        dispatch(updateTask(task));
        return task;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to update task";
        dispatch(setError(errorMessage));
        throw err;
      }
    },
    [dispatch]
  );

  const deleteTaskItem = useCallback(
    async (taskId: string) => {
      dispatch(setError(null));

      try {
        await tasksService.deleteTask(taskId);
        dispatch(deleteTask(taskId));
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to delete task";
        dispatch(setError(errorMessage));
        throw err;
      }
    },
    [dispatch]
  );

  const completeTask = useCallback(
    async (taskId: string) => {
      dispatch(setError(null));

      try {
        const task = await tasksService.completeTask(taskId);
        dispatch(updateTask(task));
        return task;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to complete task";
        dispatch(setError(errorMessage));
        throw err;
      }
    },
    [dispatch]
  );

  const applyFilters = useCallback(
    (status?: TaskStatus, priority?: TaskPriority) => {
      dispatch(setFilters({ status, priority }));
    },
    [dispatch]
  );

  const getFilteredTasks = (): Task[] => {
    return tasks.filter((task) => {
      if (filters.status && task.status !== filters.status) {
        return false;
      }
      if (
        filters.priority &&
        task.priority !== filters.priority &&
        task.ai_priority !== filters.priority
      ) {
        return false;
      }
      return true;
    });
  };

  return {
    // State
    tasks,
    filteredTasks: getFilteredTasks(),
    filters,
    isLoading,
    error,
    totalCount,
    skip,
    limit,

    // Actions
    fetchTasks,
    getTask,
    createTask,
    updateTask: updateTaskItem,
    deleteTask: deleteTaskItem,
    completeTask,
    applyFilters,
    clearTasks: () => dispatch(clearTasks()),
  };
};
