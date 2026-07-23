/** TanStack Query hooks for comments, reports, and notifications. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { communityApi } from "@/lib/community-api";
import { useAuthStore } from "@/stores/auth";

// --- Comments ---------------------------------------------------------------
export function useComments(promptId: string) {
  return useQuery({
    queryKey: ["comments", promptId],
    queryFn: () => communityApi.listComments(promptId),
    enabled: Boolean(promptId),
  });
}

export function useAddComment(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: string) => communityApi.addComment(promptId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["comments", promptId] }),
  });
}

export function useDeleteComment(promptId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (commentId: string) => communityApi.deleteComment(commentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["comments", promptId] }),
  });
}

// --- Reports / moderation ---------------------------------------------------
export function useReportPrompt(promptId: string) {
  return useMutation({
    mutationFn: (reason: string) => communityApi.report(promptId, reason),
  });
}

export function useReports(status?: string) {
  return useQuery({
    queryKey: ["reports", status ?? "all"],
    queryFn: () => communityApi.listReports(status),
  });
}

export function useUpdateReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: "resolved" | "dismissed" }) =>
      communityApi.updateReport(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reports"] }),
  });
}

// --- Notifications ----------------------------------------------------------
export function useUnreadCount() {
  const user = useAuthStore((s) => s.user);
  return useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: () => communityApi.unreadCount(),
    enabled: Boolean(user),
    refetchInterval: 60_000,
  });
}

export function useNotifications(enabled: boolean) {
  return useQuery({
    queryKey: ["notifications", "list"],
    queryFn: () => communityApi.notifications(),
    enabled,
  });
}

export function useMarkNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => communityApi.markRead(),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
