/** TanStack Query hooks for teams. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { teamsApi } from "@/lib/teams-api";
import { useAuthStore } from "@/stores/auth";

export function useTeams() {
  const user = useAuthStore((s) => s.user);
  return useQuery({
    queryKey: ["teams"],
    queryFn: () => teamsApi.list(),
    enabled: Boolean(user),
  });
}

export function useCreateTeam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) => teamsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["teams"] }),
  });
}

export function useTeam(id: string) {
  return useQuery({
    queryKey: ["teams", id],
    queryFn: () => teamsApi.get(id),
    enabled: Boolean(id),
  });
}

export function useTeamPrompts(id: string) {
  return useQuery({
    queryKey: ["teams", id, "prompts"],
    queryFn: () => teamsApi.prompts(id),
    enabled: Boolean(id),
  });
}

export function useAddMember(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (username: string) => teamsApi.addMember(id, username),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["teams", id] }),
  });
}

export function useRemoveMember(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => teamsApi.removeMember(id, userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["teams", id] }),
  });
}
