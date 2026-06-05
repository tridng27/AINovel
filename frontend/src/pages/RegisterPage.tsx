import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useRegister } from "../hooks/useAuth";
import { getErrorMessage } from "../services/api";
import "./auth.css";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);
  const register = useRegister();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (username.trim().length < 3) {
      setLocalError("Tên người dùng phải có ít nhất 3 ký tự");
      return;
    }
    if (password.length < 8) {
      setLocalError("Mật khẩu phải có ít nhất 8 ký tự");
      return;
    }
    if (password !== confirm) {
      setLocalError("Mật khẩu nhập lại không khớp");
      return;
    }

    register.mutate({ username: username.trim(), email, password });
  };

  const errorMsg =
    localError ?? (register.isError ? getErrorMessage(register.error, "Đăng ký thất bại") : null);

  return (
    <div className="auth-wrap">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>Tạo tài khoản</h1>
        <p className="subtitle">Bắt đầu hành trình viết truyện cùng AI</p>

        {errorMsg && <div className="auth-error">{errorMsg}</div>}

        <div className="auth-field">
          <label htmlFor="username">Tên người dùng</label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <div className="auth-field">
          <label htmlFor="confirm">Nhập lại mật khẩu</label>
          <input
            id="confirm"
            type="password"
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
          />
        </div>

        <button className="auth-btn" type="submit" disabled={register.isPending}>
          {register.isPending ? "Đang tạo tài khoản…" : "Đăng ký"}
        </button>

        <p className="auth-foot">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </p>
      </form>
    </div>
  );
}
