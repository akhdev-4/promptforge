/** Project / module / component API wrappers. */

import { apiFetch } from "@/lib/api";
import { apiUrl } from "@/lib/config";
import type {
  ComponentCatalogItem,
  KitCategory,
  KitTemplate,
  Page,
  ProjectSummary,
  ProjectTemplate,
  ProjectTree,
  TemplateUpsertInput,
} from "@/types";

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

  // --- Starter template (codebase pointer) ---
  getTemplate: (id: string) =>
    apiFetch<ProjectTemplate>(`/projects/${id}/template`, { auth: false }),

  upsertTemplate: (id: string, data: TemplateUpsertInput) =>
    apiFetch<ProjectTemplate>(`/projects/${id}/template`, { method: "PUT", body: data }),

  deleteTemplate: (id: string) =>
    apiFetch<void>(`/projects/${id}/template`, { method: "DELETE" }),

  // --- Starter Kits catalog ---
  browseTemplates: (category?: KitCategory, page = 1, size = 60) => {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (category) params.set("category", category);
    return apiFetch<Page<KitTemplate>>(`/projects/templates?${params}`, { auth: false });
  },

  /** Direct URL for the browser to download a kit's codebase zip. */
  templateDownloadUrl: (id: string, ref?: string) =>
    apiUrl(`/projects/${id}/template/download${ref ? `?ref=${encodeURIComponent(ref)}` : ""}`),
};
