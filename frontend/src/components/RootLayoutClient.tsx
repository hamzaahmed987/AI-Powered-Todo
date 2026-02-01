"use client";

import { useAuthModal } from "@/contexts/AuthContext";
import AuthModal from "@/components/AuthModal";

export default function RootLayoutClient({ children }: { children: React.ReactNode }) {
  const { isAuthModalOpen, authTab, closeAuthModal } = useAuthModal();

  return (
    <>
      {children}
      <AuthModal isOpen={isAuthModalOpen} onClose={closeAuthModal} initialTab={authTab} />
    </>
  );
}
