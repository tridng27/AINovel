import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useLogout } from "../hooks/useAuth";
import { useAuthStore } from "../store/authStore";

export default function Topbar() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const navigate = useNavigate();
  const [q, setQ] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    navigate(q.trim() ? `/search?q=${encodeURIComponent(q.trim())}` : "/search");
  };

  return (
    <header className="topbar">
      <form className="topbar-search" onSubmit={submit}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Tìm truyện, tác giả, thể loại..."
        />
      </form>

      <div className="topbar-right">
        {user ? (
          <>
            <span className="topbar-user">@{user.username}</span>
            <button className="topbar-btn" onClick={logout}>
              Đăng xuất
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Đăng nhập</Link>
            <Link to="/register" className="topbar-cta">
              Đăng ký
            </Link>
          </>
        )}
      </div>
    </header>
  );
}
