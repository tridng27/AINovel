import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { authService } from "./services/auth";
import { useAuthStore } from "./store/authStore";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import NovelDetailPage from "./pages/NovelDetailPage";
import ChapterPage from "./pages/ChapterPage";
import EditorPage from "./pages/EditorPage";
import ProfilePage from "./pages/ProfilePage";
import SearchPage from "./pages/SearchPage";
import AdminPage from "./pages/AdminPage";
import NotFoundPage from "./pages/NotFoundPage";

export default function App() {
  const { accessToken, user, setUser } = useAuthStore();

  // Khi tải lại trang: nếu đã có token nhưng chưa có hồ sơ, lấy lại từ /auth/me.
  useEffect(() => {
    if (accessToken && !user) {
      authService
        .me()
        .then(({ data }) => setUser(data))
        .catch(() => {});
    }
  }, [accessToken, user, setUser]);

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/novels/:slug" element={<NovelDetailPage />} />
          <Route path="/novels/:slug/chapters/:number" element={<ChapterPage />} />
          <Route path="/write/:novelId" element={<EditorPage />} />
          <Route path="/users/:username" element={<ProfilePage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Route>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
