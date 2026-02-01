"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { IoLogOut, IoCheckmarkDone, IoClose, IoWarning } from "react-icons/io5";
import { useAuth } from "@/hooks/useAuth";
import { useAppDispatch } from "@/redux/hooks";
import { clearAuth } from "@/redux/slices/authSlice";
import { showToast } from "@/utils/toastUtils";
import ChatBot from "@/components/ChatBot";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { isAuthenticated, user } = useAuth();
  const [isChecking, setIsChecking] = useState(true);
  const [isSignOutModalOpen, setIsSignOutModalOpen] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  useEffect(() => {
    // Give redux-persist time to rehydrate from localStorage
    const checkAuthTimer = setTimeout(() => {
      // Check if we have a token in localStorage (fallback check)
      const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('accessToken');

      if (!isAuthenticated && !hasToken && !isLoggingOut) {
        router.push("/auth/login");
      }
      setIsChecking(false);
    }, 100); // Small delay to allow rehydration

    return () => clearTimeout(checkAuthTimer);
  }, [isAuthenticated, router, isLoggingOut]);

  // Check both Redux state AND localStorage before redirecting
  const hasToken = typeof window !== 'undefined' && !!localStorage.getItem('accessToken');
  const isUserAuthenticated = isAuthenticated || hasToken;

  // Don't render until we've checked auth
  if (isChecking) {
    return null;
  }

  if (!isUserAuthenticated) {
    return null;
  }

  const handleConfirmLogout = () => {
    setIsLoggingOut(true);
    dispatch(clearAuth());
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user");
    setIsSignOutModalOpen(false);
    showToast.logoutSuccess();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white bg-opacity-80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5">
          <div className="flex justify-between items-center gap-4">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-blue-500/20 flex-shrink-0">
                <IoCheckmarkDone className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h1 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent truncate">
                  AI Todo
                </h1>
                <p className="text-xs sm:text-sm text-gray-500 truncate">
                  Welcome, <span className="font-semibold text-gray-700">{user?.full_name || user?.email || "User"}</span>
                </p>
              </div>
            </div>
            <button
              onClick={() => setIsSignOutModalOpen(true)}
              className="px-4 sm:px-6 py-2.5 sm:py-3 text-sm sm:text-base font-semibold text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 hover:border-red-300 rounded-lg transition duration-200 flex items-center gap-2 whitespace-nowrap group"
            >
              <IoLogOut className="w-5 h-5 group-hover:translate-x-0.5 transition duration-200" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        {children}
      </main>

      {/* Sign Out Confirmation Modal */}
      {isSignOutModalOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-transparent backdrop-blur-sm z-40 transition-opacity animate-in fade-in duration-300"
            onClick={() => setIsSignOutModalOpen(false)}
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-gray-100 animate-in zoom-in-95 duration-300 overflow-hidden">
              {/* Header */}
              <div className="sticky top-0 z-20 bg-gradient-to-r from-white to-red-50 border-b border-gray-200 px-6 py-5 flex justify-between items-center backdrop-blur-xl">
                <h2 className="text-xl font-bold text-gray-900">Sign Out</h2>
                <button
                  onClick={() => setIsSignOutModalOpen(false)}
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
                  Are you sure?
                </p>
                <p className="text-center text-sm text-gray-600 mb-8">
                  You'll need to log in again to access your tasks and AI features.
                </p>

                {/* Buttons - Same Row */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setIsSignOutModalOpen(false)}
                    className="flex-1 px-4 py-3 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition duration-200 transform hover:scale-105"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmLogout}
                    className="flex-1 px-4 py-3 text-sm font-bold text-white bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 rounded-lg transition duration-200 shadow-lg shadow-red-500/20 hover:shadow-red-500/40 transform hover:scale-105 flex items-center justify-center gap-2"
                  >
                    <IoLogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ChatBot - Only shown to authenticated users */}
      <ChatBot />
    </div>
  );
}
