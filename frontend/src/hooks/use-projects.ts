/** TanStack Query hooks for the project hierarchy. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ApiError } from "@/lib/api";
import { projectsApi } from "@/lib/projects-api";

export const projectKeys = {
  all: ["projects"] as const,
  list: ["projects", "list"] as const,
  components: ["projects", "components"] as const,
  tree: (id: string) => ["projects", "tree", id] as const,
  template: (id: string) => ["project-template", id] as const,
};

/** A project's starter-template metadata, or `null` if it isn't a kit. */
export function useProjectTemplate(id: string) {
  return useQuery({
    queryKey: projectKeys.template(id),
    queryFn: async () => {
      try {
        return await projectsApi.getTemplate(id);
      } catch (e) {
        if (e instanceof ApiError && e.status === 404) return null;
        throw e;
      }
    },
    enabled: Boolean(id),
  });
}

export function useProjects() {
  return useQuery({ queryKey: projectKeys.list, queryFn: () => projectsApi.list() });
}

export function useComponents() {
  return useQuery({
    queryKey: projectKeys.components,
    queryFn: () => projectsApi.listComponents(),
  });
}

/** All starter kits (projects that have a codebase). Shared with the Kits page. */
export function useStarterKits() {
  return useQuery({ queryKey: ["kits"], queryFn: () => projectsApi.browseTemplates() });
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

export function useUpdateProject(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { name?: string; description?: string | null }) =>
      projectsApi.update(id, data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: projectKeys.tree(id) });
      void qc.invalidateQueries({ queryKey: projectKeys.list });
    },
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => projectsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.list }),
  });
}
