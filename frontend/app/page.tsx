"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  IoCheckmarkDone,
  IoMic,
  IoSync,
  IoShield,
  IoLogIn,
  IoPersonAdd,
  IoArrowForward,
} from "react-icons/io5";
import { useAuthModal } from "@/contexts/AuthContext";

export default function Home() {
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);
  const { openAuthModal } = useAuthModal();

  useEffect(() => {
    setIsClient(true);
    // Check if user has auth token
    const token = localStorage.getItem("accessToken");
    if (token) {
      router.push("/dashboard");
    }
  }, [router]);

  if (!isClient) {
    return null;
  }

  const handleSignIn = () => {
    openAuthModal("login");
  };

  const handleCreateAccount = () => {
    openAuthModal("register");
  };

  const features = [
    {
      title: "Smart Tasks",
      description: "AI-powered priority suggestions",
      icon: <IoCheckmarkDone className="w-8 h-8" />,
      color: "from-blue-500 to-cyan-500",
    },
    {
      title: "Voice Control",
      description: "Manage tasks by speaking",
      icon: <IoMic className="w-8 h-8" />,
      color: "from-purple-500 to-pink-500",
    },
    {
      title: "Real-time Sync",
      description: "Access anywhere, anytime",
      icon: <IoSync className="w-8 h-8" />,
      color: "from-green-500 to-emerald-500",
    },
    {
      title: "Secure",
      description: "Your data protected",
      icon: <IoShield className="w-8 h-8" />,
      color: "from-orange-500 to-red-500",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 text-gray-900 overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-blue-50" />
        <div className="absolute top-0 -left-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" />
        <div className="absolute top-40 -right-40 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" />
        <div className="absolute -bottom-40 left-40 w-80 h-80 bg-cyan-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-pulse" />
      </div>

      {/* Header */}
      <header className="border-b border-gray-200 bg-white bg-opacity-80 backdrop-blur-xl sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition duration-300">
              <IoCheckmarkDone className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              AI Todo
            </h1>
          </div>

          {/* Right Side Buttons */}
          <div className="flex gap-2 sm:gap-3">
            <button
              onClick={handleSignIn}
              className="group flex items-center gap-2 px-4 sm:px-6 py-2.5 text-sm sm:text-base font-semibold text-blue-600 hover:text-blue-700 border border-blue-300 hover:border-blue-500 rounded-lg hover:bg-blue-50 transition duration-300"
            >
              <IoLogIn className="w-5 h-5" />
              <span className="hidden sm:inline">Sign In</span>
            </button>
            <button
              onClick={handleCreateAccount}
              className="group flex items-center gap-2 px-4 sm:px-6 py-2.5 text-sm sm:text-base font-semibold text-white bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 rounded-lg shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition duration-300"
            >
              <IoPersonAdd className="w-5 h-5" />
              <span className="hidden sm:inline">Register</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-12 sm:py-16">
        <div className="w-full max-w-6xl">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Side - Intro Section */}
            <div className="text-center lg:text-left">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6 leading-tight">
                <span className="block text-gray-900">Manage Your Tasks</span>
                <span className="block bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                  Smarter, Faster, Better
                </span>
              </h2>
              <p className="text-base sm:text-lg lg:text-lg text-gray-600 max-w-2xl leading-relaxed mb-10">
                AI-powered task management with voice commands and real-time synchronization. Organize your work like never before.
              </p>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handleCreateAccount}
                  className="group flex items-center justify-center gap-3 px-8 py-4 text-base sm:text-lg font-bold text-white bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 rounded-xl shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition duration-300 transform hover:scale-105"
                >
                  Get Started
                  <IoArrowForward className="w-5 h-5 group-hover:translate-x-1 transition duration-300" />
                </button>
                <button
                  onClick={handleSignIn}
                  className="group flex items-center justify-center gap-3 px-8 py-4 text-base sm:text-lg font-bold text-blue-600 border-2 border-blue-300 hover:border-blue-500 rounded-xl hover:bg-blue-50 transition duration-300 transform hover:scale-105"
                >
                  Sign In
                </button>
              </div>
            </div>

            {/* Right Side - Features Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="group relative bg-white bg-opacity-60 backdrop-blur-xl border border-white border-opacity-40 hover:border-opacity-60 rounded-2xl p-6 transition duration-300 hover:transform hover:scale-105 overflow-hidden shadow-sm hover:shadow-lg"
                >
                  {/* Gradient overlay on hover */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-5 transition duration-300`} />

                  <div className="relative z-10">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center shadow-lg mb-4 text-white`}>
                      {feature.icon}
                    </div>
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-2 text-left">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 text-sm text-left leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>

    </div>
  );
}
