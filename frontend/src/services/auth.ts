import { api } from "./api";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

export const authService = {
  register: (username: string, email: string, password: string) =>
    api.post<TokenResponse>("/auth/register", { username, email, password }),

  login: (email: string, password: string) =>
    api.post<TokenResponse>("/auth/login", { email, password }),

  refresh: (refresh_token: string) =>
    api.post<TokenResponse>("/auth/refresh", { refresh_token }),

  logout: (refresh_token: string) =>
    api.post("/auth/logout", { refresh_token }),

  me: () => api.get("/auth/me"),
};
