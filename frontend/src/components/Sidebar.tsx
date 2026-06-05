import { NavLink } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

interface Item {
  to: string;
  icon: string;
  label: string;
  soon?: boolean;
}

const MAIN: Item[] = [
  { to: "/", icon: "🏠", label: "Trang chủ" },
  { to: "/search", icon: "🧭", label: "Khám phá" },
  { to: "/search", icon: "📚", label: "Thể loại" },
];

const LIBRARY: Item[] = [
  { to: "#", icon: "📖", label: "Thư viện", soon: true },
  { to: "#", icon: "🕘", label: "Lịch sử đọc", soon: true },
  { to: "#", icon: "🔖", label: "Bookmark", soon: true },
];

export default function Sidebar() {
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="sidebar">
      <NavLink to="/" className="sidebar-brand">
        AINovel
      </NavLink>

      <nav className="sidebar-nav">
        {MAIN.map((it) => (
          <NavLink key={it.label} to={it.to} end={it.to === "/"} className="sidebar-link">
            <span className="sidebar-ic">{it.icon}</span>
            {it.label}
          </NavLink>
        ))}

        <div className="sidebar-section">Cá nhân</div>
        {LIBRARY.map((it) => (
          <span key={it.label} className="sidebar-link disabled">
            <span className="sidebar-ic">{it.icon}</span>
            {it.label}
            <span className="sidebar-soon">sắp có</span>
          </span>
        ))}

        {user?.role === "admin" && (
          <>
            <div className="sidebar-section">Quản trị</div>
            <NavLink to="/admin" className="sidebar-link">
              <span className="sidebar-ic">⭐</span>
              Trang quản trị
            </NavLink>
          </>
        )}
      </nav>
    </aside>
  );
}
