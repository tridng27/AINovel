import { api } from "./api";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  role: string;
  avatar_url: string | null;
  is_verified: boolean;
}

export interface RegisterResponse extends UserResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authService = {
  // /register tạo user và tự đăng nhập luôn (trả cả thông tin user lẫn token).
  register: (username: string, email: string, password: string) =>
    api.post<RegisterResponse>("/auth/register", { username, email, password }),

  login: (email: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { email, password }),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>("/auth/refresh", { refresh_token }),

  logout: (refresh_token: string) =>
    api.post("/auth/logout", { refresh_token }),

  me: () => api.get<UserResponse>("/auth/me"),
};
