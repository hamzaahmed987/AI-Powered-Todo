import { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "@/redux/hooks";
import { setAccessToken, setUser } from "@/redux/slices/authSlice";

/**
 * Hook to initialize auth state from localStorage
 * Ensures Redux state is synced with persisted localStorage data
 * This is useful when redux-persist hasn't fully rehydrated yet
 */
export const useInitializeAuth = () => {
  const dispatch = useAppDispatch();
  const { accessToken, isAuthenticated } = useAppSelector((state) => state.auth);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    // Sync localStorage to Redux if not already set
    if (!accessToken && typeof window !== "undefined") {
      try {
        const storedToken = localStorage.getItem("accessToken");
        const storedUser = localStorage.getItem("user");

        if (storedToken) {
          dispatch(setAccessToken(storedToken));
        }

        if (storedUser) {
          try {
            const user = JSON.parse(storedUser);
            dispatch(setUser(user));
          } catch (error) {
            console.warn("Failed to parse stored user:", error);
          }
        }
      } catch (error) {
        console.warn("Failed to initialize auth from localStorage:", error);
      }
    }

    setIsInitialized(true);
  }, [dispatch, accessToken]);

  return {
    isInitialized,
    accessToken,
    isAuthenticated,
  };
};
