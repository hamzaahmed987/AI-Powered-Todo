"use client";

import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { createTask as createTaskThunk } from "@/redux/thunks/taskThunks";
import { useFormik } from "formik";
import { taskValidationSchema, type TaskFormValues } from "@/lib/validations";
import { FormField } from "@/components/FormField";

interface TaskFormProps {
  onClose: () => void;
}

const initialValues: TaskFormValues = {
  title: "",
  description: "",
  deadline: undefined,
  priority: "medium",
  estimated_duration: undefined,
};

export default function TaskForm({ onClose }: TaskFormProps) {
  const dispatch = useAppDispatch();
  const error = useAppSelector((state) => state.tasks.error);
  const isLoading = useAppSelector((state) => state.tasks.isLoading);

  const formik = useFormik<TaskFormValues>({
    initialValues,
    validationSchema: taskValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        const result = await dispatch(
          createTaskThunk({
            title: values.title,
            description: values.description || undefined,
            deadline: values.deadline ? values.deadline : undefined,
            priority: values.priority || "medium",
            estimated_duration: values.estimated_duration || undefined,
          })
        );

        if (createTaskThunk.fulfilled.match(result)) {
          formik.resetForm();
          onClose();
        }
      } catch (err) {
        console.error("Failed to create task:", err);
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <form onSubmit={formik.handleSubmit} className="space-y-4 sm:space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Title Field */}
      <FormField
        field={{ name: "title", value: formik.values.title, onChange: formik.handleChange, onBlur: formik.handleBlur }}
        form={formik}
        label="Task Title"
        placeholder="What needs to be done?"
        required
      />

      {/* Priority Field */}
      <div>
        <label htmlFor="priority" className="block text-gray-700 font-medium mb-1 sm:mb-2 text-sm sm:text-base">
          Priority Level
        </label>
        <select
          id="priority"
          name="priority"
          value={formik.values.priority}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
          className="w-full px-3 sm:px-4 py-2 sm:py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm sm:text-base"
        >
          <option value="low">Low Priority</option>
          <option value="medium">Medium Priority</option>
          <option value="high">High Priority</option>
        </select>
      </div>

      {/* Description Field */}
      <FormField
        field={{ name: "description", value: formik.values.description, onChange: formik.handleChange, onBlur: formik.handleBlur }}
        form={formik}
        label="Description"
        placeholder="Add more details about this task..."
        type="textarea"
        rows={3}
        helperText="Optional: Provide additional context for your task"
      />

      {/* Deadline Field */}
      <FormField
        field={{ name: "deadline", value: formik.values.deadline, onChange: formik.handleChange, onBlur: formik.handleBlur }}
        form={formik}
        label="Deadline"
        type="datetime-local"
        helperText="Optional: Set a deadline for this task"
      />

      {/* Estimated Duration Field */}
      <FormField
        field={{
          name: "estimated_duration",
          value: formik.values.estimated_duration || "",
          onChange: (e) => {
            const value = e.target.value;
            formik.setFieldValue("estimated_duration", value ? parseInt(value) : undefined);
          },
          onBlur: formik.handleBlur
        }}
        form={formik}
        label="Estimated Duration"
        type="number"
        placeholder="Minutes"
        helperText="Optional: Estimated time to complete this task (in minutes)"
      />

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3 pt-2">
        <button
          type="submit"
          disabled={isLoading || formik.isSubmitting}
          className="flex-1 px-4 sm:px-6 py-2.5 sm:py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition duration-200 text-sm sm:text-base"
        >
          {isLoading || formik.isSubmitting ? "Creating..." : "Create Task"}
        </button>
        <button
          type="button"
          onClick={onClose}
          className="flex-1 px-4 sm:px-6 py-2.5 sm:py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold rounded-lg transition duration-200 text-sm sm:text-base"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
