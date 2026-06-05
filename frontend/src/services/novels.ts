import { api } from "./api";

export interface Novel {
  id: string;
  author_id: string;
  title: string;
  slug: string;
  synopsis: string | null;
  cover_image_url: string | null;
  status: string;
  view_count: number;
  word_count: number;
  rating_avg: number;
  chapter_count: number;
  created_at: string;
  updated_at: string;
}

export interface NovelList {
  items: Novel[];
  total: number;
  page: number;
  page_size: number;
}

export type NovelSort = "updated_at" | "view_count" | "rating_avg";

export const novelService = {
  list: (params?: { page?: number; status?: string; genre_id?: number; sort?: NovelSort; page_size?: number }) =>
    api.get<NovelList>("/novels", { params }),

  get: (slug: string) => api.get<Novel>(`/novels/${slug}`),

  create: (data: { title: string; synopsis?: string; genre_ids: number[]; tags: string[] }) =>
    api.post<Novel>("/novels", data),

  update: (id: string, data: object) => api.put<Novel>(`/novels/${id}`, data),

  listChapters: (slug: string) => api.get(`/novels/${slug}/chapters`),

  getChapter: (slug: string, number: number) => api.get(`/novels/${slug}/chapters/${number}`),

  createChapter: (novelId: string, data: { title: string; content: string }) =>
    api.post(`/novels/${novelId}/chapters`, data),

  updateChapter: (novelId: string, chapterId: string, data: object) =>
    api.put(`/novels/${novelId}/chapters/${chapterId}`, data),
};
