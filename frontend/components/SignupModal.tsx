"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useFormik } from "formik";
import { registerValidationSchema, type RegisterFormValues } from "@/lib/validations";
import { FormField } from "@/components/FormField";
import { IoAlertCircle } from "react-icons/io5";

const initialValues: RegisterFormValues = {
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
};

interface SignupModalProps {
  onSwitchToLogin: () => void;
  onClose?: () => void;
}

export default function SignupModal({ onSwitchToLogin, onClose }: SignupModalProps) {
  const router = useRouter();
  const { register, isLoading, error } = useAuth();

  const formik = useFormik<RegisterFormValues>({
    initialValues,
    validationSchema: registerValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await register({
          name: values.name,
          email: values.email,
          password: values.password,
        });
        onClose?.();
        router.push("/dashboard");
      } catch (err) {
        console.error("Registration failed:", err);
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <div className="w-full">
      {/* Error Alert */}
      {error && (
        <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded-lg backdrop-blur-sm">
          <p className="text-red-700 font-semibold flex items-center gap-2 text-xs">
            <IoAlertCircle className="w-3 h-3 flex-shrink-0" />
            <span>{error}</span>
          </p>
        </div>
      )}

      <form onSubmit={formik.handleSubmit}>
        {/* First Row - Name and Email (2 columns on desktop, 1 on mobile) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 mb-2">
          {/* Full Name Field */}
          <FormField
            field={{ name: "name", value: formik.values.name, onChange: formik.handleChange, onBlur: formik.handleBlur }}
            form={formik}
            label="Name"
            type="text"
            placeholder="John Doe"
          />

          {/* Email Field */}
          <FormField
            field={{ name: "email", value: formik.values.email, onChange: formik.handleChange, onBlur: formik.handleBlur }}
            form={formik}
            label="Email"
            type="email"
            placeholder="you@example.com"
          />
        </div>

        {/* Second Row - Password and Confirm */}
        <div className="grid grid-cols-1 gap-2 mb-2">
          {/* Password Field */}
          <FormField
            field={{ name: "password", value: formik.values.password, onChange: formik.handleChange, onBlur: formik.handleBlur }}
            form={formik}
            label="Password"
            type="password"
            placeholder="Strong password"
          />

          {/* Confirm Password Field */}
          <FormField
            field={{ name: "confirmPassword", value: formik.values.confirmPassword, onChange: formik.handleChange, onBlur: formik.handleBlur }}
            form={formik}
            label="Confirm Password"
            type="password"
            placeholder="Confirm password"
          />
        </div>

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
              Creating Account...
            </span>
          ) : (
            "Create Account"
          )}
        </button>
      </form>
    </div>
  );
}
