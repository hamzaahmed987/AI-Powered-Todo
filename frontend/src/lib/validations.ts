import * as Yup from "yup";

// ===== Login Validation =====
export interface LoginFormValues {
  email: string;
  password: string;
}

export const loginValidationSchema = Yup.object().shape({
  email: Yup.string()
    .email("Please enter a valid email address")
    .required("Email is required"),
  password: Yup.string()
    .min(12, "Password must be at least 12 characters")
    .required("Password is required"),
});

// ===== Register Validation =====
export interface RegisterFormValues {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export const registerValidationSchema = Yup.object().shape({
  name: Yup.string()
    .min(2, "Name must be at least 2 characters")
    .max(50, "Name must not exceed 50 characters")
    .required("Name is required"),
  email: Yup.string()
    .email("Please enter a valid email address")
    .required("Email is required"),
  password: Yup.string()
    .min(12, "Password must be at least 12 characters")
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      "Password must contain uppercase, lowercase, and number"
    )
    .required("Password is required"),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref("password")], "Passwords must match")
    .required("Please confirm your password"),
});

// ===== Task Form Validation =====
export interface TaskFormValues {
  title: string;
  description?: string;
  deadline?: string;
  priority: "low" | "medium" | "high";
  estimated_duration?: number;
}

export const taskValidationSchema = Yup.object().shape({
  title: Yup.string()
    .min(3, "Title must be at least 3 characters")
    .max(100, "Title must not exceed 100 characters")
    .required("Task title is required"),
  description: Yup.string()
    .max(500, "Description must not exceed 500 characters")
    .optional(),
  deadline: Yup.string()
    .test("valid-date", "Please enter a valid date", (value) => {
      if (!value) return true;
      return new Date(value) > new Date();
    })
    .optional(),
  priority: Yup.string()
    .oneOf(["low", "medium", "high"], "Please select a valid priority")
    .required("Priority is required"),
  estimated_duration: Yup.number()
    .min(1, "Duration must be at least 1 minute")
    .max(1440, "Duration must not exceed 1440 minutes (24 hours)")
    .nullable()
    .optional(),
});
