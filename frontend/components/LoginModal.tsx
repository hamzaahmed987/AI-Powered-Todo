"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useFormik } from "formik";
import { loginValidationSchema, type LoginFormValues } from "@/lib/validations";
import { FormField } from "@/components/FormField";
import { IoAlertCircle } from "react-icons/io5";

const initialValues: LoginFormValues = {
  email: "",
  password: "",
};

interface LoginModalProps {
  onSwitchToSignup: () => void;
  onClose?: () => void;
}

export default function LoginModal({ onSwitchToSignup, onClose }: LoginModalProps) {
  const router = useRouter();
  const { login, isLoading, error } = useAuth();

  const formik = useFormik<LoginFormValues>({
    initialValues,
    validationSchema: loginValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await login(values);
        onClose?.();
        router.push("/dashboard");
      } catch (err) {
        console.error("Login failed:", err);
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <div className="w-full">
      {/* Error Alert */}
      {error && (
        <div className="mb-2.5 p-2 bg-red-50 border border-red-200 rounded-lg backdrop-blur-sm">
          <p className="text-red-700 font-semibold flex items-center gap-2 text-xs">
            <IoAlertCircle className="w-3 h-3 flex-shrink-0" />
            <span>{error}</span>
          </p>
        </div>
      )}

      <form onSubmit={formik.handleSubmit} className="space-y-2.5">
        {/* Email Field */}
        <FormField
          field={{ name: "email", value: formik.values.email, onChange: formik.handleChange, onBlur: formik.handleBlur }}
          form={formik}
          label="Email Address"
          type="email"
          placeholder="you@example.com"
        />

        {/* Password Field */}
        <FormField
          field={{ name: "password", value: formik.values.password, onChange: formik.handleChange, onBlur: formik.handleBlur }}
          form={formik}
          label="Password"
          type="password"
          placeholder="Enter your password"
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || formik.isSubmitting}
          className="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 px-4 rounded-lg transition duration-200 text-xs mt-2.5 shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transform hover:scale-105 disabled:transform disabled:scale-100"
        >
          {isLoading || formik.isSubmitting ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
          ) : (
            "Sign In"
          )}
        </button>
      </form>
    </div>
  );
}
