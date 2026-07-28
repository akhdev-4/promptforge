/** Teams / workspaces API. */

import { apiFetch } from "@/lib/api";
import type {
  InviteCreated,
  InviteInfo,
  PromptSummary,
  TeamDetail,
  TeamInvite,
  TeamSummary,
} from "@/types";

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

  // --- Invitations ---
  invite: (id: string, email: string) =>
    apiFetch<InviteCreated>(`/teams/${id}/invites`, { method: "POST", body: { email } }),
  listInvites: (id: string) => apiFetch<TeamInvite[]>(`/teams/${id}/invites`),
  revokeInvite: (id: string, inviteId: string) =>
    apiFetch<void>(`/teams/${id}/invites/${inviteId}`, { method: "DELETE" }),
  getInvite: (token: string) => apiFetch<InviteInfo>(`/invites/${token}`, { auth: false }),
  acceptInvite: (token: string) =>
    apiFetch<TeamDetail>(`/invites/${token}/accept`, { method: "POST" }),
};
