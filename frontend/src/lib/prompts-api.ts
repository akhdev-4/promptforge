/** Prompt API wrappers over `apiFetch`. */

import { apiFetch } from "@/lib/api";
import type {
  AssetCreateInput,
  Page,
  PromptAsset,
  PromptCreateInput,
  PromptDetail,
  PromptSort,
  PromptStatus,
  PromptSummary,
  PromptType,
  PromptUpdateInput,
  PromptVersion,
  VersionCompare,
  VersionCreateInput,
} from "@/types";

export interface PromptListParams {
  page?: number;
  size?: number;
  q?: string;
  prompt_type?: PromptType;
  framework?: string;
  language?: string;
  ai_model?: string;
  status?: PromptStatus;
  author_id?: string;
  category_id?: string;
  exclude_category_id?: string;
  component_id?: string;
  tags?: string[];
  sort?: PromptSort;
}

function toQuery(params: Record<string, unknown>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    if (Array.isArray(v)) {
      for (const item of v) sp.append(k, String(item));
    } else {
      sp.set(k, String(v));
    }
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export const promptsApi = {
  list: (params: PromptListParams = {}) =>
    apiFetch<Page<PromptSummary>>(
      `/prompts${toQuery(params as Record<string, unknown>)}`,
      { auth: false },
    ),

  // Authenticated when logged in (so is_bookmarked / is_liked reflect the
  // current user), still works anonymously for public viewers.
  get: (id: string) => apiFetch<PromptDetail>(`/prompts/${id}`),

  related: (id: string, limit = 6) =>
    apiFetch<PromptSummary[]>(`/prompts/${id}/related?limit=${limit}`, { auth: false }),

  create: (data: PromptCreateInput) =>
    apiFetch<PromptDetail>("/prompts", { method: "POST", body: data }),

  update: (id: string, data: PromptUpdateInput) =>
    apiFetch<PromptDetail>(`/prompts/${id}`, { method: "PATCH", body: data }),

  remove: (id: string) =>
    apiFetch<void>(`/prompts/${id}`, { method: "DELETE" }),

  copy: (id: string) =>
    apiFetch<{ id: string; content: string; copies_count: number }>(
      `/prompts/${id}/copy`,
      { method: "POST", auth: false },
    ),

  fork: (id: string) =>
    apiFetch<PromptDetail>(`/prompts/${id}/fork`, { method: "POST" }),

  listVersions: (id: string) =>
    apiFetch<PromptVersion[]>(`/prompts/${id}/versions`, { auth: false }),

  addVersion: (id: string, data: VersionCreateInput) =>
    apiFetch<PromptVersion>(`/prompts/${id}/versions`, { method: "POST", body: data }),

  compareVersions: (id: string, from: number, to: number) =>
    apiFetch<VersionCompare>(
      `/prompts/${id}/versions/compare?from=${from}&to=${to}`,
      { auth: false },
    ),

  listAssets: (id: string) =>
    apiFetch<PromptAsset[]>(`/prompts/${id}/assets`, { auth: false }),

  addAsset: (id: string, data: AssetCreateInput) =>
    apiFetch<PromptAsset>(`/prompts/${id}/assets`, { method: "POST", body: data }),

  removeAsset: (id: string, assetId: string) =>
    apiFetch<void>(`/prompts/${id}/assets/${assetId}`, { method: "DELETE" }),
};
