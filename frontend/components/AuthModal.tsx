'use client';

import { useState } from 'react';
import { IoClose } from 'react-icons/io5';
import LoginModal from '@/components/LoginModal';
import SignupModal from '@/components/SignupModal';

type AuthMode = 'login' | 'signup';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: AuthMode;
}

export default function AuthModal({ isOpen, onClose, initialMode = 'login' }: AuthModalProps) {
  const [authMode, setAuthMode] = useState<AuthMode>(initialMode);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-transparent backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[calc(90vh+50px)] overflow-y-auto border border-gray-100 animate-in zoom-in-95 duration-300">
        {/* Header with Close Button */}
        <div className="sticky top-0 z-20 bg-gradient-to-r from-white to-blue-50 border-b border-gray-200 px-6 py-3.5 flex justify-between items-center backdrop-blur-xl">
          <h2 className="text-lg font-bold text-gray-900">
            {authMode === 'login' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition duration-200 text-gray-500 hover:text-gray-700"
            aria-label="Close modal"
          >
            <IoClose className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Tabs */}
        <div className="flex border-b border-gray-200 px-0 bg-gray-50">
          <button
            onClick={() => setAuthMode('login')}
            className={`flex-1 px-6 py-3 font-semibold text-sm transition-all relative ${
              authMode === 'login'
                ? 'text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Sign In
            {authMode === 'login' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-600" />
            )}
          </button>
          <button
            onClick={() => setAuthMode('signup')}
            className={`flex-1 px-6 py-3 font-semibold text-sm transition-all relative ${
              authMode === 'signup'
                ? 'text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Register
            {authMode === 'signup' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-600" />
            )}
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-5 bg-white">
          {authMode === 'login' ? (
            <LoginModal onSwitchToSignup={() => setAuthMode('signup')} onClose={onClose} />
          ) : (
            <SignupModal onSwitchToLogin={() => setAuthMode('login')} onClose={onClose} />
          )}
        </div>
      </div>
    </div>
  );
}
