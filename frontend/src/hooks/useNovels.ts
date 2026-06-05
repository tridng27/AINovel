import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { novelService } from "../services/novels";

export function useNovelList(params?: Parameters<typeof novelService.list>[0]) {
  return useQuery({
    queryKey: ["novels", params],
    queryFn: () => novelService.list(params).then((r) => r.data),
  });
}

export function useNovel(slug: string) {
  return useQuery({
    queryKey: ["novel", slug],
    queryFn: () => novelService.get(slug).then((r) => r.data),
    enabled: !!slug,
  });
}

export function useChapters(slug: string) {
  return useQuery({
    queryKey: ["chapters", slug],
    queryFn: () => novelService.listChapters(slug).then((r) => r.data),
    enabled: !!slug,
  });
}

export function useChapter(slug: string, number: number) {
  return useQuery({
    queryKey: ["chapter", slug, number],
    queryFn: () => novelService.getChapter(slug, number).then((r) => r.data),
    enabled: !!slug && !!number,
  });
}

export function useCreateNovel() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: novelService.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["novels"] }),
  });
}
