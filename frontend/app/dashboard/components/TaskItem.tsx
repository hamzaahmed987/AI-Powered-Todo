"use client";

import { useState } from "react";
import { IoTrash, IoCheckmarkDone, IoHourglassOutline, IoStopwatch, IoChevronDown, IoChevronUp, IoWarning, IoClose } from "react-icons/io5";
import { Task, TaskStatus, TaskPriority } from "@/redux/slices/taskSlice";
import { useTasks } from "@/hooks/useTasks";

interface TaskItemProps {
  task: Task;
}

const priorityColors: Record<string, string> = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
};

const statusColors: Record<TaskStatus, string> = {
  pending: "bg-gray-50",
  in_progress: "bg-blue-50",
  completed: "bg-green-50",
};

export default function TaskItem({ task }: TaskItemProps) {
  const { updateTask, deleteTask, isLoading, error } = useTasks();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const getPriority = (): string => {
    return task.priority || "medium";
  };

  const handleStatusChange = async (newStatus: TaskStatus) => {
    setIsUpdating(true);
    try {
      await updateTask(task.id, { status: newStatus });
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteClick = () => {
    setIsDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await deleteTask(task.id);
      setIsDeleteModalOpen(false);
    } catch (err) {
      // Error is handled in useTasks hook
    }
  };

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return "";
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  const priority = getPriority();

  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case "pending":
        return <IoHourglassOutline className="w-4 h-4" />;
      case "in_progress":
        return <IoStopwatch className="w-4 h-4" />;
      case "completed":
        return <IoCheckmarkDone className="w-4 h-4" />;
    }
  };

  return (
    <div
      className={`p-4 sm:p-5 rounded-xl border border-gray-200 transition hover:shadow-md ${statusColors[task.status]}`}
    >
      {/* Task Header */}
      <div className="flex flex-col sm:flex-row items-start justify-between gap-3 sm:gap-4">
        <div className="flex-1 min-w-0">
          {/* Title and Priority */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3 mb-3">
            <h3
              className={`text-base sm:text-lg font-bold break-words ${
                task.status === "completed"
                  ? "line-through text-gray-400"
                  : "text-gray-900"
              }`}
            >
              {task.title}
            </h3>
            <span
              className={`inline-flex px-3 py-1.5 text-xs font-bold rounded-lg whitespace-nowrap ${
                priorityColors[priority]
              }`}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </span>
          </div>

          {/* Task Metadata */}
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600 mb-3">
            <div className="flex items-center gap-1.5">
              {getStatusIcon(task.status)}
              <span className="font-medium">
                {task.status === "in_progress" ? "In Progress" : task.status.charAt(0).toUpperCase() + task.status.slice(1)}
              </span>
            </div>
            {task.deadline && (
              <span className="whitespace-nowrap">
                Due: <span className="text-gray-900 font-medium">{formatDate(task.deadline)}</span>
              </span>
            )}
            {(task.estimated_duration || task.ai_estimated_duration) && (
              <div className="flex items-center gap-1.5">
                <IoStopwatch className="w-4 h-4" />
                <span className="whitespace-nowrap">
                  Est:
                  {task.estimated_duration && <span className="text-gray-900 font-medium"> {task.estimated_duration}m</span>}
                  {task.estimated_duration && task.ai_estimated_duration && <span> | </span>}
                  {task.ai_estimated_duration && <span className="text-blue-600 font-medium"> AI: {task.ai_estimated_duration}m</span>}
                </span>
              </div>
            )}
          </div>

          {/* AI Suggestions */}
          {(task.ai_priority || task.ai_estimated_duration) && (
            <div className="flex flex-wrap gap-2 mb-3">
              {task.ai_priority && task.ai_priority !== task.priority && (
                <div className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-blue-50 text-blue-800 rounded-full border border-blue-200">
                  <IoWarning className="w-3 h-3" />
                  <span>AI suggests: {task.ai_priority}</span>
                </div>
              )}
              {task.ai_estimated_duration && (
                <div className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium bg-blue-50 text-blue-800 rounded-full border border-blue-200">
                  <IoStopwatch className="w-3 h-3" />
                  <span>AI est: {task.ai_estimated_duration}m</span>
                </div>
              )}
            </div>
          )}

          {/* Description */}
          {task.description && (
            <>
              {!isExpanded && (
                <p className="text-gray-700 line-clamp-2 text-xs sm:text-sm mb-2">
                  {task.description}
                </p>
              )}
              {isExpanded && (
                <p className="text-gray-700 text-xs sm:text-sm mb-2">
                  {task.description}
                </p>
              )}
            </>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 w-full sm:w-auto">
          {task.description && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="px-3 py-2 text-xs font-semibold text-gray-600 hover:text-gray-900 hover:bg-white rounded-lg transition whitespace-nowrap flex items-center gap-1 border border-gray-200"
            >
              {isExpanded ? <IoChevronUp className="w-4 h-4" /> : <IoChevronDown className="w-4 h-4" />}
              {isExpanded ? "Less" : "More"}
            </button>
          )}
          <button
            onClick={handleDeleteClick}
            disabled={isUpdating}
            className="px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50 border border-red-200 hover:border-red-300 flex items-center gap-1 whitespace-nowrap"
          >
            <IoTrash className="w-4 h-4" />
            Delete
          </button>
        </div>
      </div>

      {/* Status Selector */}
      <div className="mt-4 flex flex-wrap gap-2">
        {(["pending", "in_progress", "completed"] as TaskStatus[]).map(
          (status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              disabled={isUpdating}
              className={`px-4 py-2.5 text-xs sm:text-sm font-semibold rounded-lg transition flex items-center gap-2 ${
                task.status === status
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/20"
                  : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400"
              } disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap`}
            >
              {getStatusIcon(status)}
              {status === "in_progress" ? "In Progress" : status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          )
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-xs font-medium">{error}</p>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-transparent backdrop-blur-sm z-40 transition-opacity animate-in fade-in duration-300"
            onClick={() => setIsDeleteModalOpen(false)}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm border border-gray-100 animate-in zoom-in-95 duration-300">
              {/* Header */}
              <div className="sticky top-0 z-20 bg-gradient-to-r from-white to-red-50 border-b border-gray-200 px-6 py-3.5 flex justify-between items-center backdrop-blur-xl">
                <h2 className="text-lg font-bold text-gray-900">Delete Task</h2>
                <button
                  onClick={() => setIsDeleteModalOpen(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition duration-200 text-gray-500 hover:text-gray-700"
                  title="Close"
                >
                  <IoClose className="w-6 h-6" />
                </button>
              </div>

              {/* Content */}
              <div className="p-8 bg-white">
                {/* Warning Icon */}
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-red-100 to-red-50 flex items-center justify-center shadow-lg shadow-red-100/50">
                    <IoWarning className="w-8 h-8 text-red-600" />
                  </div>
                </div>

                {/* Message */}
                <p className="text-center text-gray-700 font-bold text-lg mb-2">
                  Delete this task?
                </p>
                <p className="text-center text-sm text-gray-600 mb-8">
                  <span className="font-semibold text-gray-900">"{task.title}"</span> will be permanently deleted. This action cannot be undone.
                </p>

                {/* Buttons - Same Row */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setIsDeleteModalOpen(false)}
                    className="flex-1 px-4 py-3 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition duration-200 transform hover:scale-105"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmDelete}
                    disabled={isUpdating}
                    className="flex-1 px-4 py-3 text-sm font-bold text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-lg transition duration-200 shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transform hover:scale-105 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <IoTrash className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
