import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import {
  adminService,
  type AdminComment,
  type AdminNovel,
  type AdminStats,
  type AdminUser,
} from "../services/admin";
import { getErrorMessage } from "../services/api";
import { useAuthStore } from "../store/authStore";
import "./admin.css";

type Tab = "dashboard" | "users" | "novels" | "comments";

export default function AdminPage() {
  const { user, accessToken } = useAuthStore();
  const [tab, setTab] = useState<Tab>("dashboard");

  // Chưa đăng nhập → về login. Đã đăng nhập nhưng đang nạp hồ sơ → chờ.
  if (!accessToken) return <Navigate to="/login" replace />;
  if (!user) return <div className="admin-wrap">Đang tải…</div>;
  if (user.role !== "admin")
    return <div className="admin-wrap admin-denied">⛔ Bạn không có quyền truy cập trang quản trị.</div>;

  return (
    <div className="admin-wrap">
      <h1>Trang quản trị</h1>
      <nav className="admin-tabs">
        <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>
          Tổng quan
        </button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>
          Người dùng
        </button>
        <button className={tab === "novels" ? "active" : ""} onClick={() => setTab("novels")}>
          Truyện
        </button>
        <button className={tab === "comments" ? "active" : ""} onClick={() => setTab("comments")}>
          Bình luận
        </button>
      </nav>

      {tab === "dashboard" && <DashboardTab />}
      {tab === "users" && <UsersTab currentUserId={user.id} />}
      {tab === "novels" && <NovelsTab />}
      {tab === "comments" && <CommentsTab />}
    </div>
  );
}

// ── Dashboard ───────────────────────────────────────────────────────────────
function DashboardTab() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    adminService
      .stats()
      .then(({ data }) => setStats(data))
      .catch((e) => setError(getErrorMessage(e)));
  }, []);

  if (error) return <div className="admin-error">{error}</div>;
  if (!stats) return <div>Đang tải…</div>;

  const cards: [string, number][] = [
    ["Người dùng", stats.users],
    ["Quản trị viên", stats.admins],
    ["Truyện", stats.novels],
    ["Chương", stats.chapters],
    ["Bình luận", stats.comments],
  ];
  return (
    <div className="admin-cards">
      {cards.map(([label, value]) => (
        <div className="admin-card" key={label}>
          <div className="admin-card-value">{value}</div>
          <div className="admin-card-label">{label}</div>
        </div>
      ))}
    </div>
  );
}

// ── Users ───────────────────────────────────────────────────────────────────
function UsersTab({ currentUserId }: { currentUserId: string }) {
  const [rows, setRows] = useState<AdminUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    adminService
      .users()
      .then(({ data }) => setRows(data))
      .catch((e) => setError(getErrorMessage(e)));

  useEffect(() => {
    load();
  }, []);

  const changeRole = async (id: string, role: string) => {
    try {
      await adminService.setRole(id, role);
      await load();
    } catch (e) {
      alert(getErrorMessage(e));
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Xóa người dùng này?")) return;
    try {
      await adminService.deleteUser(id);
      await load();
    } catch (e) {
      alert(getErrorMessage(e));
    }
  };

  if (error) return <div className="admin-error">{error}</div>;
  return (
    <table className="admin-table">
      <thead>
        <tr>
          <th>Username</th>
          <th>Email</th>
          <th>Vai trò</th>
          <th>Xác thực</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((u) => (
          <tr key={u.id}>
            <td>{u.username}</td>
            <td>{u.email}</td>
            <td>
              <select value={u.role} onChange={(e) => changeRole(u.id, e.target.value)}>
                <option value="reader">reader</option>
                <option value="author">author</option>
                <option value="admin">admin</option>
              </select>
            </td>
            <td>{u.is_verified ? "✓" : "—"}</td>
            <td>
              {u.id !== currentUserId && (
                <button className="admin-del" onClick={() => remove(u.id)}>
                  Xóa
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Novels ──────────────────────────────────────────────────────────────────
function NovelsTab() {
  const [rows, setRows] = useState<AdminNovel[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    adminService
      .novels()
      .then(({ data }) => setRows(data))
      .catch((e) => setError(getErrorMessage(e)));

  useEffect(() => {
    load();
  }, []);

  const remove = async (id: string) => {
    if (!confirm("Xóa truyện này?")) return;
    try {
      await adminService.deleteNovel(id);
      await load();
    } catch (e) {
      alert(getErrorMessage(e));
    }
  };

  if (error) return <div className="admin-error">{error}</div>;
  if (rows.length === 0) return <p className="admin-muted">Chưa có truyện nào.</p>;
  return (
    <table className="admin-table">
      <thead>
        <tr>
          <th>Tiêu đề</th>
          <th>Tác giả</th>
          <th>Trạng thái</th>
          <th>Lượt xem</th>
          <th>Số chương</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((n) => (
          <tr key={n.id}>
            <td>{n.title}</td>
            <td>{n.author_username ?? "—"}</td>
            <td>{n.status}</td>
            <td>{n.view_count}</td>
            <td>{n.chapter_count}</td>
            <td>
              <button className="admin-del" onClick={() => remove(n.id)}>
                Xóa
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Comments ────────────────────────────────────────────────────────────────
function CommentsTab() {
  const [rows, setRows] = useState<AdminComment[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    adminService
      .comments()
      .then(({ data }) => setRows(data))
      .catch((e) => setError(getErrorMessage(e)));

  useEffect(() => {
    load();
  }, []);

  const remove = async (id: string) => {
    if (!confirm("Xóa bình luận này?")) return;
    try {
      await adminService.deleteComment(id);
      await load();
    } catch (e) {
      alert(getErrorMessage(e));
    }
  };

  if (error) return <div className="admin-error">{error}</div>;
  if (rows.length === 0) return <p className="admin-muted">Chưa có bình luận nào.</p>;
  return (
    <table className="admin-table">
      <thead>
        <tr>
          <th>Người viết</th>
          <th>Nội dung</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {rows.map((c) => (
          <tr key={c.id}>
            <td>{c.username ?? "—"}</td>
            <td>{c.body}</td>
            <td>
              <button className="admin-del" onClick={() => remove(c.id)}>
                Xóa
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
