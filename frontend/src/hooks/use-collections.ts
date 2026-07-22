/** TanStack Query hooks for collections and interactions. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { collectionsApi, interactionsApi } from "@/lib/collections-api";
import { promptKeys } from "@/hooks/use-prompts";

export const collectionKeys = {
  publicList: ["collections", "public"] as const,
  mine: ["collections", "mine"] as const,
  detail: (id: string) => ["collections", "detail", id] as const,
  bookmarks: ["bookmarks"] as const,
};

export function usePublicCollections() {
  return useQuery({
    queryKey: collectionKeys.publicList,
    queryFn: () => collectionsApi.listPublic(),
  });
}

export function useMyCollections(enabled = true) {
  return useQuery({
    queryKey: collectionKeys.mine,
    queryFn: () => collectionsApi.mine(),
    enabled,
  });
}

export function useCollection(id: string) {
  return useQuery({
    queryKey: collectionKeys.detail(id),
    queryFn: () => collectionsApi.get(id),
    enabled: Boolean(id),
  });
}

export function useCreateCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string; is_public?: boolean }) =>
      collectionsApi.create(data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: collectionKeys.mine });
      void qc.invalidateQueries({ queryKey: collectionKeys.publicList });
    },
  });
}

export function useDeleteCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => collectionsApi.remove(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: collectionKeys.mine });
      void qc.invalidateQueries({ queryKey: collectionKeys.publicList });
    },
  });
}

export function useAddToCollection() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ collectionId, promptId }: { collectionId: string; promptId: string }) =>
      collectionsApi.addItem(collectionId, promptId),
    onSuccess: (_data, vars) => {
      void qc.invalidateQueries({ queryKey: collectionKeys.detail(vars.collectionId) });
      void qc.invalidateQueries({ queryKey: collectionKeys.mine });
    },
  });
}

export function useRemoveFromCollection(collectionId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (promptId: string) => collectionsApi.removeItem(collectionId, promptId),
    onSuccess: () => qc.invalidateQueries({ queryKey: collectionKeys.detail(collectionId) }),
  });
}

export function useMyBookmarks() {
  return useQuery({
    queryKey: collectionKeys.bookmarks,
    queryFn: () => interactionsApi.myBookmarks(),
  });
}

export function useToggleLike(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => interactionsApi.toggleLike(promptId),
    onSuccess: () => qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) }),
  });
}

export function useToggleBookmark(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => interactionsApi.toggleBookmark(promptId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      void qc.invalidateQueries({ queryKey: collectionKeys.bookmarks });
    },
  });
}

export function useRatePrompt(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (stars: number | null) =>
      stars === null ? interactionsApi.unrate(promptId) : interactionsApi.rate(promptId, stars),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.detail(promptId) });
      void qc.invalidateQueries({ queryKey: promptKeys.all });
    },
  });
}
