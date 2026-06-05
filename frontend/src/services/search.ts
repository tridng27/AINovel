import { api } from "./api";

export interface SearchHit {
  id: string;
  title: string;
  slug: string;
  synopsis: string | null;
  author_username: string | null;
  cover_url: string | null;
  view_count: number;
  rating_avg: number | null;
}

export interface SearchResult {
  hits: SearchHit[];
  total: number;
  page: number;
  total_pages: number;
}

export const searchService = {
  novels: (q: string, params?: { genre_id?: number; status?: string; page?: number }) =>
    api.get<SearchResult>("/search/novels", { params: { q, ...params } }),
};
