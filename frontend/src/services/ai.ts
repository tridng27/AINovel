import { api } from "./api";

export const aiService = {
  streamCompletion: (novelId: string, text: string): EventSource => {
    const token = localStorage.getItem("access_token");
    const params = new URLSearchParams({ token: token ?? "", prompt: text });
    const url = `/api/v1/ai/novels/${novelId}/complete?${params.toString()}`;
    return new EventSource(url);
  },

  enqueueContinuityCheck: (novelId: string) =>
    api.post(`/ai/novels/${novelId}/continuity-check`),

  enqueueArcPlan: (novelId: string, chapter_count: number) =>
    api.post(`/ai/novels/${novelId}/arc-plan`, { chapter_count }),

  getJob: (jobId: string) => api.get(`/ai/jobs/${jobId}`),

  getContext: (novelId: string) => api.get(`/ai/novels/${novelId}/context`),
};
