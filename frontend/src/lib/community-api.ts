/** Comments, reports, moderation, and notifications API. */

import { apiFetch } from "@/lib/api";
import type { AppNotification, Comment, Report } from "@/types";

export const communityApi = {
  // Comments
  listComments: (promptId: string) =>
    apiFetch<Comment[]>(`/prompts/${promptId}/comments`, { auth: false }),
  addComment: (promptId: string, body: string) =>
    apiFetch<Comment>(`/prompts/${promptId}/comments`, { method: "POST", body: { body } }),
  deleteComment: (commentId: string) =>
    apiFetch<void>(`/comments/${commentId}`, { method: "DELETE" }),

  // Reports
  report: (promptId: string, reason: string) =>
    apiFetch<{ reported: boolean }>(`/prompts/${promptId}/report`, {
      method: "POST",
      body: { reason },
    }),
  listReports: (status?: string) =>
    apiFetch<Report[]>(`/moderation/reports${status ? `?status=${status}` : ""}`),
  updateReport: (reportId: string, status: "resolved" | "dismissed") =>
    apiFetch<Report>(`/moderation/reports/${reportId}`, { method: "PATCH", body: { status } }),

  // Notifications
  notifications: (limit = 30) =>
    apiFetch<AppNotification[]>(`/users/me/notifications?limit=${limit}`),
  unreadCount: () => apiFetch<{ unread: number }>(`/users/me/notifications/unread-count`),
  markRead: () => apiFetch<void>(`/users/me/notifications/read`, { method: "POST" }),
};
