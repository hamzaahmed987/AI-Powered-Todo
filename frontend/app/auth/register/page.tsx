"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useFormik } from "formik";
import { registerValidationSchema, type RegisterFormValues } from "@/lib/validations";
import { FormField } from "@/components/FormField";

const initialValues: RegisterFormValues = {
  name: "",
  email: "",
  password: "",
  confirmPassword: "",
};

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, isAuthenticated } = useAuth();

  useEffect(() => {
    // Check both Redux state and localStorage for token
    const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('accessToken');

    if (isAuthenticated || hasToken) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  const formik = useFormik<RegisterFormValues>({
    initialValues,
    validationSchema: registerValidationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        // Register returns with auto-login token
        const result = await register({
          name: values.name,
          email: values.email,
          password: values.password,
        });

        // User is now authenticated, redirect to dashboard
        // No manual login needed!
        router.push("/dashboard");
      } catch (err) {
        console.error("Registration failed:", err);
        // Error is already shown in the form
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-600 to-emerald-800 flex items-center justify-center p-4">
      <div className="w-full max-w-5xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left Side - Benefits Section */}
          <div className="text-white order-2 lg:order-1">
            <div className="mb-8">
              <h1 className="text-4xl sm:text-5xl lg:text-5xl font-bold mb-6 leading-tight">
                Join <span className="text-green-200">AI Todo</span><br />
                Today
              </h1>
              <p className="text-lg sm:text-xl text-green-100 mb-8">
                Start organizing your tasks smarter with AI-powered insights
              </p>
            </div>

            {/* Benefits Grid */}
            <div className="space-y-6">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-400 bg-opacity-20">
                    <svg className="h-6 w-6 text-green-200" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">AI-Powered Insights</h3>
                  <p className="text-green-100">Get smart priority recommendations</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-400 bg-opacity-20">
                    <svg className="h-6 w-6 text-green-200" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">Easy Organization</h3>
                  <p className="text-green-100">Organize and track tasks effortlessly</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-400 bg-opacity-20">
                    <svg className="h-6 w-6 text-green-200" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">Secure & Private</h3>
                  <p className="text-green-100">Your data is encrypted and protected</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-green-400 bg-opacity-20">
                    <svg className="h-6 w-6 text-green-200" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-bold mb-1">Always Accessible</h3>
                  <p className="text-green-100">Access your tasks anytime, anywhere</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Registration Form */}
          <div className="bg-white rounded-2xl shadow-2xl p-5 sm:p-6 lg:p-7 order-1 lg:order-2">
            <h2 className="text-xl sm:text-2xl lg:text-2xl font-bold text-gray-900 mb-1">
              Create Account
            </h2>
            <p className="text-gray-600 text-xs sm:text-sm mb-4">
              Sign up to get started with AI Todo
            </p>

            {/* Error Alert */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 rounded">
                <p className="text-red-700 font-semibold flex items-center gap-2 text-xs sm:text-sm">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  {error}
                </p>
              </div>
            )}

            <form onSubmit={formik.handleSubmit} className="space-y-3 sm:space-y-4">
              {/* Full Name Field */}
              <FormField
                field={{ name: "name", value: formik.values.name, onChange: formik.handleChange, onBlur: formik.handleBlur }}
                form={formik}
                label="Full Name"
                placeholder="John Doe"
              />

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
                placeholder="Create a strong password"
                helperText="12 chars: uppercase, lowercase, number"
              />

              {/* Confirm Password Field */}
              <FormField
                field={{ name: "confirmPassword", value: formik.values.confirmPassword, onChange: formik.handleChange, onBlur: formik.handleBlur }}
                form={formik}
                label="Confirm Password"
                type="password"
                placeholder="Re-enter password"
              />

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading || formik.isSubmitting}
                className="w-full bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2 sm:py-2.5 px-4 rounded-lg transition duration-200 text-sm sm:text-base mt-4"
              >
                {isLoading || formik.isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating...
                  </span>
                ) : (
                  "Create Account"
                )}
              </button>
            </form>

            {/* Login Link */}
            <p className="text-center text-gray-600 text-xs sm:text-sm mt-4">
              Already have an account?{" "}
              <Link
                href="/auth/login"
                className="text-green-600 hover:text-green-700 font-bold hover:underline"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
