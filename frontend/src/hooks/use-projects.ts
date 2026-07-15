/** TanStack Query hooks for the project hierarchy. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { projectsApi } from "@/lib/projects-api";

export const projectKeys = {
  all: ["projects"] as const,
  list: ["projects", "list"] as const,
  tree: (id: string) => ["projects", "tree", id] as const,
};

export function useProjects() {
  return useQuery({ queryKey: projectKeys.list, queryFn: () => projectsApi.list() });
}

export function useProjectTree(id: string) {
  return useQuery({
    queryKey: projectKeys.tree(id),
    queryFn: () => projectsApi.tree(id),
    enabled: Boolean(id),
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) => projectsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.list }),
  });
}

export function useAddModule(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      projectsApi.addModule(projectId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.tree(projectId) }),
  });
}

export function useAddComponent(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ moduleId, name }: { moduleId: string; name: string }) =>
      projectsApi.addComponent(moduleId, { name }),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.tree(projectId) }),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.list }),
  });
}
