/** Category and tag API wrappers. */

import { apiFetch } from "@/lib/api";
import type { Category, CategoryNode, Tag } from "@/types";

export const categoriesApi = {
  tree: () => apiFetch<CategoryNode[]>("/categories/tree", { auth: false }),
  list: () => apiFetch<Category[]>("/categories", { auth: false }),
  create: (data: { name: string; parent_id?: string | null; description?: string }) =>
    apiFetch<Category>("/categories", { method: "POST", body: data }),
};

export const tagsApi = {
  list: () => apiFetch<Tag[]>("/tags", { auth: false }),
  popular: (limit = 30) =>
    apiFetch<Tag[]>(`/tags/popular?limit=${limit}`, { auth: false }),
};
