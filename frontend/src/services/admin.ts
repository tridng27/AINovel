import { api } from "./api";

export interface AdminStats {
  users: number;
  novels: number;
  chapters: number;
  comments: number;
  admins: number;
}

export interface AdminUser {
  id: string;
  username: string;
  email: string;
  role: string;
  is_verified: boolean;
  created_at: string;
}

export interface AdminNovel {
  id: string;
  title: string;
  slug: string;
  author_username: string | null;
  status: string;
  view_count: number;
  chapter_count: number;
  created_at: string;
}

export interface AdminComment {
  id: string;
  body: string;
  username: string | null;
  chapter_id: string;
  created_at: string;
}

export const adminService = {
  stats: () => api.get<AdminStats>("/admin/stats"),

  users: () => api.get<AdminUser[]>("/admin/users"),
  setRole: (id: string, role: string) => api.patch<AdminUser>(`/admin/users/${id}/role`, { role }),
  deleteUser: (id: string) => api.delete(`/admin/users/${id}`),

  novels: () => api.get<AdminNovel[]>("/admin/novels"),
  deleteNovel: (id: string) => api.delete(`/admin/novels/${id}`),

  comments: () => api.get<AdminComment[]>("/admin/comments"),
  deleteComment: (id: string) => api.delete(`/admin/comments/${id}`),
};
