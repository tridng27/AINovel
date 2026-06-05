import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import type { UserResponse } from "../services/auth";
import { useAuthStore } from "../store/authStore";

/** Lưu token + tải hồ sơ người dùng hiện tại vào store. */
async function establishSession(
  access: string,
  refresh: string,
  setTokens: (a: string, r: string) => void,
  setUser: (u: UserResponse | null) => void,
) {
  setTokens(access, refresh);
  const { data: user } = await authService.me();
  setUser(user);
}

export function useLogin() {
  const { setTokens, setUser } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      const { data } = await authService.login(email, password);
      await establishSession(data.access_token, data.refresh_token, setTokens, setUser);
    },
    onSuccess: () => navigate("/"),
  });
}

export function useRegister() {
  const { setTokens, setUser } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async ({
      username,
      email,
      password,
    }: {
      username: string;
      email: string;
      password: string;
    }) => {
      // /register trả về cả token lẫn thông tin user → đăng nhập luôn.
      const { data } = await authService.register(username, email, password);
      setTokens(data.access_token, data.refresh_token);
      setUser(data);
    },
    onSuccess: () => navigate("/"),
  });
}

export function useLogout() {
  const { refreshToken, logout } = useAuthStore();
  const navigate = useNavigate();
  return () => {
    if (refreshToken) authService.logout(refreshToken).catch(() => {});
    logout();
    navigate("/login");
  };
}
