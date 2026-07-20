/** TanStack Query hooks for categories and tags. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { categoriesApi, tagsApi } from "@/lib/taxonomy-api";

export const taxonomyKeys = {
  categoryTree: ["categories", "tree"] as const,
  categoryList: ["categories", "list"] as const,
  popularTags: ["tags", "popular"] as const,
};

export function useCategoryTree() {
  return useQuery({
    queryKey: taxonomyKeys.categoryTree,
    queryFn: () => categoriesApi.tree(),
    staleTime: 5 * 60_000,
  });
}

export function useCategoryList() {
  return useQuery({
    queryKey: taxonomyKeys.categoryList,
    queryFn: () => categoriesApi.list(),
    staleTime: 5 * 60_000,
  });
}

export function usePopularTags(limit = 30) {
  return useQuery({
    queryKey: [...taxonomyKeys.popularTags, limit],
    queryFn: () => tagsApi.popular(limit),
    staleTime: 60_000,
  });
}

function useInvalidateCategories() {
  const qc = useQueryClient();
  return () => {
    void qc.invalidateQueries({ queryKey: taxonomyKeys.categoryTree });
    void qc.invalidateQueries({ queryKey: taxonomyKeys.categoryList });
  };
}

export function useCreateCategory() {
  const invalidate = useInvalidateCategories();
  return useMutation({
    mutationFn: (data: { name: string; parent_id?: string | null; description?: string }) =>
      categoriesApi.create(data),
    onSuccess: invalidate,
  });
}

export function useDeleteCategory() {
  const invalidate = useInvalidateCategories();
  return useMutation({
    mutationFn: (id: string) => categoriesApi.remove(id),
    onSuccess: invalidate,
  });
}
