import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useLogin } from "../hooks/useAuth";
import { getErrorMessage } from "../services/api";
import "./auth.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    login.mutate({ email, password });
  };

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Đăng nhập</h1>
        <p className="subtitle">Chào mừng trở lại AINovel</p>

        {login.isError && (
          <div className="auth-error">{getErrorMessage(login.error, "Đăng nhập thất bại")}</div>
        )}

        <div className="auth-field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="auth-field">
          <label htmlFor="password">Mật khẩu</label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button className="auth-btn" type="submit" disabled={login.isPending}>
          {login.isPending ? "Đang đăng nhập…" : "Đăng nhập"}
        </button>

        <p className="auth-foot">
          Chưa có tài khoản? <Link to="/register">Đăng ký</Link>
        </p>
      </form>
    </div>
  );
}
