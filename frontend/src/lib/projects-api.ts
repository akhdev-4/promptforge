/** Project / module / component API wrappers. */

import { apiFetch } from "@/lib/api";
import type { ComponentCatalogItem, Page, ProjectSummary, ProjectTree } from "@/types";

export const projectsApi = {
  list: (page = 1, size = 30) =>
    apiFetch<Page<ProjectSummary>>(`/projects?page=${page}&size=${size}`, { auth: false }),

  listComponents: (page = 1, size = 60) =>
    apiFetch<Page<ComponentCatalogItem>>(`/projects/components?page=${page}&size=${size}`, {
      auth: false,
    }),

  tree: (id: string) => apiFetch<ProjectTree>(`/projects/${id}/tree`, { auth: false }),

  create: (data: { name: string; description?: string }) =>
    apiFetch<ProjectSummary>("/projects", { method: "POST", body: data }),

  remove: (id: string) => apiFetch<void>(`/projects/${id}`, { method: "DELETE" }),

  addModule: (projectId: string, data: { name: string; description?: string }) =>
    apiFetch(`/projects/${projectId}/modules`, { method: "POST", body: data }),

  deleteModule: (moduleId: string) =>
    apiFetch<void>(`/projects/modules/${moduleId}`, { method: "DELETE" }),

  addComponent: (moduleId: string, data: { name: string; description?: string }) =>
    apiFetch(`/projects/modules/${moduleId}/components`, { method: "POST", body: data }),

  deleteComponent: (componentId: string) =>
    apiFetch<void>(`/projects/components/${componentId}`, { method: "DELETE" }),
};
