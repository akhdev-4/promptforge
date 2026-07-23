/** Teams / workspaces API. */

import { apiFetch } from "@/lib/api";
import type { PromptSummary, TeamDetail, TeamSummary } from "@/types";

export const teamsApi = {
  list: () => apiFetch<TeamSummary[]>("/teams"),
  create: (data: { name: string; description?: string }) =>
    apiFetch<TeamDetail>("/teams", { method: "POST", body: data }),
  get: (id: string) => apiFetch<TeamDetail>(`/teams/${id}`),
  addMember: (id: string, username: string) =>
    apiFetch<{ added: boolean }>(`/teams/${id}/members`, {
      method: "POST",
      body: { username },
    }),
  removeMember: (id: string, userId: string) =>
    apiFetch<void>(`/teams/${id}/members/${userId}`, { method: "DELETE" }),
  prompts: (id: string) => apiFetch<PromptSummary[]>(`/teams/${id}/prompts`),
};
