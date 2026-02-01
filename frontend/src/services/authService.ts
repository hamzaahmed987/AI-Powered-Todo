import api from "./api";
import { User } from "@/redux/slices/authSlice";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  name?: string; // Frontend passes 'name', backend expects 'full_name'
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthResponse {
  status: string;
  data: AuthToken;
}

export interface UserResponse {
  status: string;
  data: User;
}

export interface RegisterResponse {
  user: User;
  access_token: string;
  token_type: string;
  expires_in: number;
}

export const authService = {
  login: async (credentials: LoginRequest): Promise<AuthToken> => {
    const response = await api.post<AuthResponse>(
      "auth/login",
      credentials
    );
    // Backend returns AuthToken directly, not wrapped in data
    const token = response.data;
    return {
      access_token: token.access_token,
      token_type: token.token_type,
      expires_in: token.expires_in,
    };
  },

  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    // Convert 'name' to 'full_name' if needed
    const registerData = {
      email: data.email,
      password: data.password,
      full_name: data.full_name || data.name,
    };

    const response = await api.post<RegisterResponse>(
      "auth/register",
      registerData
    );

    // Backend now returns both user and token
    return {
      user: response.data.user,
      access_token: response.data.access_token,
      token_type: response.data.token_type,
      expires_in: response.data.expires_in,
    };
  },

  logout: () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("user");
  },
};
