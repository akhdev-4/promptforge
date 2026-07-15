/** Collection and interaction (like/bookmark) API wrappers. */

import { apiFetch } from "@/lib/api";
import type { Collection, CollectionDetail, Page, PromptSummary } from "@/types";

export const collectionsApi = {
  listPublic: (page = 1, size = 30) =>
    apiFetch<Page<Collection>>(`/collections?page=${page}&size=${size}`, { auth: false }),

  mine: () => apiFetch<Collection[]>("/collections/mine"),

  get: (id: string) => apiFetch<CollectionDetail>(`/collections/${id}`),

  create: (data: { name: string; description?: string; is_public?: boolean }) =>
    apiFetch<Collection>("/collections", { method: "POST", body: data }),

  remove: (id: string) => apiFetch<void>(`/collections/${id}`, { method: "DELETE" }),

  addItem: (id: string, promptId: string) =>
    apiFetch<Collection>(`/collections/${id}/items`, {
      method: "POST",
      body: { prompt_id: promptId },
    }),

  removeItem: (id: string, promptId: string) =>
    apiFetch<void>(`/collections/${id}/items/${promptId}`, { method: "DELETE" }),
};

export const interactionsApi = {
  toggleLike: (promptId: string) =>
    apiFetch<{ liked: boolean; likes_count: number }>(`/prompts/${promptId}/like`, {
      method: "POST",
    }),

  toggleBookmark: (promptId: string) =>
    apiFetch<{ bookmarked: boolean }>(`/prompts/${promptId}/bookmark`, {
      method: "POST",
    }),

  myBookmarks: (page = 1, size = 30) =>
    apiFetch<Page<PromptSummary>>(`/users/me/bookmarks?page=${page}&size=${size}`),
};
