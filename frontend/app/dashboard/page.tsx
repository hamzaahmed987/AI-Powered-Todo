"use client";

import { useEffect, useState } from "react";
import { IoAdd, IoCheckmarkDone, IoHourglassOutline, IoStopwatch } from "react-icons/io5";
import { useTasks } from "@/hooks/useTasks";
import { TaskStatus, TaskPriority } from "@/redux/slices/taskSlice";
import TaskList from "./components/TaskList";
import NewTaskModal from "@/components/NewTaskModal";

export default function DashboardPage() {
  const { fetchTasks, filteredTasks, isLoading, error, applyFilters, taskStats, createTask } =
    useTasks();
  const [selectedStatus, setSelectedStatus] = useState<TaskStatus | undefined>(
    undefined
  );
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    // Fetch tasks on mount
    fetchTasks(selectedStatus);
  }, [selectedStatus, fetchTasks]);

  const handleStatusChange = (status: TaskStatus | undefined) => {
    setSelectedStatus(status);
    applyFilters(status);
  };

  const handleCreateTask = async (taskData: {
    title: string;
    description: string;
    priority: "low" | "medium" | "high" | "urgent";
    deadline?: string;
  }) => {
    setIsSubmitting(true);
    try {
      await createTask({
        title: taskData.title,
        description: taskData.description,
        deadline: taskData.deadline,
      });

      setIsModalOpen(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Page Header */}
      <div className="pb-6 border-b border-gray-200">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-2 sm:mb-3">
          My Tasks
        </h2>
        <p className="text-sm sm:text-base text-gray-600">
          Manage your tasks with AI-powered suggestions
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
          <div className="w-5 h-5 text-red-600 flex-shrink-0">!</div>
          <p className="text-red-700 text-sm font-medium">{error}</p>
        </div>
      )}

      {/* Create Task Button & Stats */}
      <div className="flex flex-col sm:flex-row gap-4 sm:items-center justify-between">
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white font-bold rounded-xl transition duration-200 text-sm sm:text-base flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:scale-105 w-full sm:w-auto"
        >
          <IoAdd className="w-5 h-5" />
          New Task
        </button>
        {taskStats && (
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400"></div>
              <span className="text-gray-600">
                Total: <span className="font-bold text-gray-900">{taskStats.total}</span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span className="text-gray-600">
                Done: <span className="font-bold text-green-600">{taskStats.completed}</span>
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span className="text-gray-600">
                In Progress: <span className="font-bold text-blue-600">{taskStats.inProgress}</span>
              </span>
            </div>
          </div>
        )}
      </div>

      {/* New Task Modal */}
      <NewTaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />

      {/* Status Filter Tabs */}
      <div className="border-b border-gray-200 overflow-x-auto">
        <div className="flex gap-2 sm:gap-4 min-w-min">
          {[
            { status: undefined, label: "All", icon: null },
            { status: "pending", label: "Pending", icon: <IoHourglassOutline className="w-4 h-4" /> },
            { status: "in_progress", label: "In Progress", icon: <IoStopwatch className="w-4 h-4" /> },
            { status: "completed", label: "Completed", icon: <IoCheckmarkDone className="w-4 h-4" /> },
          ].map(({ status, label, icon }) => (
            <button
              key={status || "all"}
              onClick={() =>
                handleStatusChange(status as TaskStatus | undefined)
              }
              className={`px-4 sm:px-5 py-3 font-semibold text-sm sm:text-base border-b-2 transition duration-200 whitespace-nowrap flex items-center gap-2 ${
                selectedStatus === status
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {icon}
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tasks List */}
      <div>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-600 text-sm sm:text-base">
              Loading tasks...
            </div>
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600 text-base sm:text-lg mb-2">
              No tasks yet
            </p>
            <p className="text-xs sm:text-sm text-gray-500">
              Create your first task to get started
            </p>
          </div>
        ) : (
          <TaskList tasks={filteredTasks} />
        )}
      </div>
    </div>
  );
}
