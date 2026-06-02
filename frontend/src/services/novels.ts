import { api } from "./api";

export const novelService = {
  list: (params?: { page?: number; status?: string; genre_id?: number; sort?: string }) =>
    api.get("/novels", { params }),

  get: (slug: string) => api.get(`/novels/${slug}`),

  create: (data: { title: string; synopsis?: string; genre_ids: number[]; tags: string[] }) =>
    api.post("/novels", data),

  update: (id: string, data: object) => api.put(`/novels/${id}`, data),

  listChapters: (slug: string) => api.get(`/novels/${slug}/chapters`),

  getChapter: (slug: string, number: number) =>
    api.get(`/novels/${slug}/chapters/${number}`),

  createChapter: (novelId: string, data: { title: string; content: string }) =>
    api.post(`/novels/${novelId}/chapters`, data),

  updateChapter: (novelId: string, chapterId: string, data: object) =>
    api.put(`/novels/${novelId}/chapters/${chapterId}`, data),
};
