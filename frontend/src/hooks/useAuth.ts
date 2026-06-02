import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { authService } from "../services/auth";
import { useAuthStore } from "../store/authStore";

export function useLogin() {
  const { setTokens } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authService.login(email, password),
    onSuccess: ({ data }) => {
      setTokens(data.access_token, data.refresh_token);
      navigate("/");
    },
  });
}

export function useRegister() {
  const { setTokens } = useAuthStore();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: ({ username, email, password }: { username: string; email: string; password: string }) =>
      authService.register(username, email, password),
    onSuccess: ({ data }) => {
      setTokens(data.access_token, data.refresh_token);
      navigate("/");
    },
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
