import { useAppSelector } from "@/redux/hooks";

/**
 * Hook to get the authentication token from Redux state
 * This is the preferred way to get the token instead of localStorage
 */
export const useToken = () => {
  const accessToken = useAppSelector((state) => state.auth.accessToken);
  return accessToken;
};
