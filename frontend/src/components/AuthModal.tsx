"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useFormik } from "formik";
import { loginValidationSchema, registerValidationSchema, type LoginFormValues, type RegisterFormValues } from "@/lib/validations";
import { FormField } from "@/components/FormField";
import { useAuth } from "@/hooks/useAuth";
import { showToast } from "@/utils/toastUtils";
import { IoClose } from "react-icons/io5";

type AuthTab = "login" | "register";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: AuthTab;
}

export default function AuthModal({ isOpen, onClose, initialTab = "login" }: AuthModalProps) {
  const router = useRouter();
  const { login, register, isLoading, error } = useAuth();
  const [activeTab, setActiveTab] = useState<AuthTab>(initialTab);

  // Login form
  const loginFormik = useFormik<LoginFormValues>({
    initialValues: { email: "", password: "" },
    validationSchema: loginValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await login(values);
        showToast.loginSuccess();
        onClose();
        router.push("/dashboard");
      } catch (err) {
        showToast.loginError(error);
        console.error("Login failed:", err);
      } finally {
        setSubmitting(false);
      }
    },
  });

  // Register form
  const registerFormik = useFormik<RegisterFormValues>({
    initialValues: { name: "", email: "", password: "", confirmPassword: "" },
    validationSchema: registerValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        await register({
          name: values.name,
          email: values.email,
          password: values.password,
        });
        showToast.registerSuccess();
        onClose();
        router.push("/dashboard");
      } catch (err) {
        showToast.registerError(error);
        console.error("Registration failed:", err);
      } finally {
        setSubmitting(false);
      }
    },
  });

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 z-10 bg-gradient-to-r from-indigo-600 to-blue-600 px-6 py-5 flex justify-between items-center">
            <h2 className="text-xl font-bold text-white">
              {activeTab === "login" ? "Sign In" : "Create Account"}
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition text-white"
              title="Close"
            >
              <IoClose className="w-6 h-6" />
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("login")}
              className={`flex-1 py-3 font-semibold transition ${
                activeTab === "login"
                  ? "border-b-2 border-indigo-600 text-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setActiveTab("register")}
              className={`flex-1 py-3 font-semibold transition ${
                activeTab === "register"
                  ? "border-b-2 border-indigo-600 text-indigo-600"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              Sign Up
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === "login" ? (
              <form onSubmit={loginFormik.handleSubmit} className="space-y-4">
                <FormField
                  field={{
                    name: "email",
                    value: loginFormik.values.email,
                    onChange: loginFormik.handleChange,
                    onBlur: loginFormik.handleBlur,
                  }}
                  form={loginFormik}
                  label="Email Address"
                  type="email"
                  placeholder="you@example.com"
                />

                <FormField
                  field={{
                    name: "password",
                    value: loginFormik.values.password,
                    onChange: loginFormik.handleChange,
                    onBlur: loginFormik.handleBlur,
                  }}
                  form={loginFormik}
                  label="Password"
                  type="password"
                  placeholder="Enter your password"
                />

                <button
                  type="submit"
                  disabled={loginFormik.isSubmitting || isLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 px-4 rounded-lg transition duration-200"
                >
                  {loginFormik.isSubmitting || isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
            ) : (
              <form onSubmit={registerFormik.handleSubmit} className="space-y-4">
                <FormField
                  field={{
                    name: "name",
                    value: registerFormik.values.name,
                    onChange: registerFormik.handleChange,
                    onBlur: registerFormik.handleBlur,
                  }}
                  form={registerFormik}
                  label="Full Name"
                  type="text"
                  placeholder="Your name"
                />

                <FormField
                  field={{
                    name: "email",
                    value: registerFormik.values.email,
                    onChange: registerFormik.handleChange,
                    onBlur: registerFormik.handleBlur,
                  }}
                  form={registerFormik}
                  label="Email Address"
                  type="email"
                  placeholder="you@example.com"
                />

                <FormField
                  field={{
                    name: "password",
                    value: registerFormik.values.password,
                    onChange: registerFormik.handleChange,
                    onBlur: registerFormik.handleBlur,
                  }}
                  form={registerFormik}
                  label="Password"
                  type="password"
                  placeholder="Minimum 12 characters"
                />

                <FormField
                  field={{
                    name: "confirmPassword",
                    value: registerFormik.values.confirmPassword,
                    onChange: registerFormik.handleChange,
                    onBlur: registerFormik.handleBlur,
                  }}
                  form={registerFormik}
                  label="Confirm Password"
                  type="password"
                  placeholder="Re-enter your password"
                />

                <button
                  type="submit"
                  disabled={registerFormik.isSubmitting || isLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 px-4 rounded-lg transition duration-200"
                >
                  {registerFormik.isSubmitting || isLoading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
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
            )}
          </div>
        </div>
      </div>
    </>
  );
}
