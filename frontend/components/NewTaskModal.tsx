"use client";

import { useState } from "react";
import { IoClose, IoAlertCircle } from "react-icons/io5";

interface NewTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (taskData: TaskFormData) => Promise<void>;
  isLoading?: boolean;
}

interface TaskFormData {
  title: string;
  description: string;
  priority: "low" | "medium" | "high" | "urgent";
  deadline?: string;
}

export default function NewTaskModal({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false,
}: NewTaskModalProps) {
  const [formData, setFormData] = useState<TaskFormData>({
    title: "",
    description: "",
    priority: "medium",
    deadline: "",
  });
  const [error, setError] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.title.trim()) {
      setError("Task title is required");
      return;
    }

    if (formData.title.length < 3) {
      setError("Task title must be at least 3 characters");
      return;
    }

    try {
      await onSubmit(formData);
      // Reset form on success
      setFormData({
        title: "",
        description: "",
        priority: "medium",
        deadline: "",
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task");
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-transparent backdrop-blur-sm z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[calc(90vh+50px)] overflow-y-auto border border-gray-100 animate-in zoom-in-95 duration-300">
          {/* Header */}
          <div className="sticky top-0 z-20 bg-gradient-to-r from-white to-blue-50 border-b border-gray-200 px-6 py-3.5 flex justify-between items-center backdrop-blur-xl">
            <h2 className="text-lg font-bold text-gray-900">Create New Task</h2>
            <button
              onClick={onClose}
              disabled={isLoading}
              className="p-2 hover:bg-gray-100 rounded-lg transition duration-200 text-gray-500 hover:text-gray-700 disabled:opacity-50"
              title="Close"
            >
              <IoClose className="w-6 h-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-5 bg-white">
            {/* Error Message */}
            {error && (
              <div className="mb-2.5 p-2 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 font-semibold flex items-center gap-2 text-xs">
                  <IoAlertCircle className="w-3 h-3 flex-shrink-0" />
                  <span>{error}</span>
                </p>
              </div>
            )}

            {/* Form Grid - 1 column on mobile, 2 columns on desktop */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-2.5 mb-2.5">
              {/* Title Field */}
              <div className="lg:col-span-2">
                <label
                  htmlFor="title"
                  className="block text-gray-700 font-semibold mb-1.5 text-sm"
                >
                  Task Title *
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="Enter task title"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-400 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 disabled:border-gray-300"
                  disabled={isLoading}
                  autoFocus
                  maxLength={100}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.title.length}/100
                </p>
              </div>

              {/* Priority Field */}
              <div>
                <label
                  htmlFor="priority"
                  className="block text-gray-700 font-semibold mb-1.5 text-sm"
                >
                  Priority
                </label>
                <select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 disabled:border-gray-300"
                  disabled={isLoading}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              {/* Deadline Field */}
              <div>
                <label
                  htmlFor="deadline"
                  className="block text-gray-700 font-semibold mb-1.5 text-sm"
                >
                  Deadline
                </label>
                <input
                  type="datetime-local"
                  id="deadline"
                  name="deadline"
                  value={formData.deadline}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 disabled:border-gray-300"
                  disabled={isLoading}
                />
              </div>

              {/* Description Field */}
              <div className="lg:col-span-2">
                <label
                  htmlFor="description"
                  className="block text-gray-700 font-semibold mb-1.5 text-sm"
                >
                  Description
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Enter task description (optional)"
                  rows={2}
                  className="w-full px-4 py-2.5 border-2 border-gray-200 rounded-lg text-sm font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-900 placeholder-gray-400 transition-all disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-400 disabled:border-gray-300 resize-none"
                  disabled={isLoading}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.description.length}/500
                </p>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-2.5">
              <button
                type="button"
                onClick={onClose}
                disabled={isLoading}
                className="flex-1 px-4 py-2.5 text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 px-4 py-2.5 text-xs font-semibold text-white bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:scale-105 disabled:transform disabled:scale-100"
              >
                {isLoading ? (
                  <>
                    <svg
                      className="w-4 h-4 animate-spin"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </>
                ) : (
                  "Create Task"
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
