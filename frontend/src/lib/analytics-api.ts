/** Analytics API wrappers. */

import { apiFetch } from "@/lib/api";
import type { PromptSummary } from "@/types";

export interface OverviewStats {
  total_prompts: number;
  total_categories: number;
  total_collections: number;
  total_projects: number;
  total_tags: number;
  total_views: number;
  total_copies: number;
  total_likes: number;
}

export interface Contributor {
  id: string;
  username: string | null;
  full_name: string | null;
  prompt_count: number;
}

export interface GrowthPoint {
  date: string;
  count: number;
}

export interface TypeCount {
  prompt_type: string;
  count: number;
}

export const analyticsApi = {
  overview: () => apiFetch<OverviewStats>("/analytics/overview", { auth: false }),
  trending: (limit = 6) =>
    apiFetch<PromptSummary[]>(`/analytics/trending?limit=${limit}`, { auth: false }),
  latest: (limit = 6) =>
    apiFetch<PromptSummary[]>(`/analytics/latest?limit=${limit}`, { auth: false }),
  contributors: (limit = 5) =>
    apiFetch<Contributor[]>(`/analytics/contributors?limit=${limit}`, { auth: false }),
  growth: (days = 30) =>
    apiFetch<GrowthPoint[]>(`/analytics/growth?days=${days}`, { auth: false }),
  byType: () => apiFetch<TypeCount[]>("/analytics/by-type", { auth: false }),
};
