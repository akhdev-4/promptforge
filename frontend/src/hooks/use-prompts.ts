/** TanStack Query hooks for prompts. */

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { promptsApi, type PromptListParams } from "@/lib/prompts-api";
import type {
  AssetCreateInput,
  PromptCreateInput,
  PromptUpdateInput,
  VersionCreateInput,
} from "@/types";

export const promptKeys = {
  all: ["prompts"] as const,
  list: (params: PromptListParams) => ["prompts", "list", params] as const,
  detail: (id: string) => ["prompts", "detail", id] as const,
  versions: (id: string) => ["prompts", "versions", id] as const,
  assets: (id: string) => ["prompts", "assets", id] as const,
};

export function usePrompts(params: PromptListParams) {
  return useQuery({
    queryKey: promptKeys.list(params),
    queryFn: () => promptsApi.list(params),
  });
}

export function usePrompt(id: string) {
  return useQuery({
    queryKey: promptKeys.detail(id),
    queryFn: () => promptsApi.get(id),
    enabled: Boolean(id),
  });
}

export function usePromptVersions(id: string) {
  return useQuery({
    queryKey: promptKeys.versions(id),
    queryFn: () => promptsApi.listVersions(id),
    enabled: Boolean(id),
  });
}

export function useRelatedPrompts(id: string) {
  return useQuery({
    queryKey: ["prompts", "related", id],
    queryFn: () => promptsApi.related(id),
    enabled: Boolean(id),
  });
}

export function useCreatePrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: PromptCreateInput) => promptsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: promptKeys.all }),
  });
}

export function useUpdatePrompt(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: PromptUpdateInput) => promptsApi.update(id, data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.detail(id) });
      void qc.invalidateQueries({ queryKey: promptKeys.all });
    },
  });
}

export function useDeletePrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => promptsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: promptKeys.all }),
  });
}

export function useAddVersion(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: VersionCreateInput) => promptsApi.addVersion(id, data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.detail(id) });
      void qc.invalidateQueries({ queryKey: promptKeys.versions(id) });
    },
  });
}

export function useForkPrompt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => promptsApi.fork(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: promptKeys.all }),
  });
}

export function usePromptAssets(id: string) {
  return useQuery({
    queryKey: promptKeys.assets(id),
    queryFn: () => promptsApi.listAssets(id),
    enabled: Boolean(id),
  });
}

export function useAddAsset(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AssetCreateInput) => promptsApi.addAsset(id, data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.assets(id) });
      void qc.invalidateQueries({ queryKey: promptKeys.detail(id) });
    },
  });
}

export function useRemoveAsset(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (assetId: string) => promptsApi.removeAsset(id, assetId),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: promptKeys.assets(id) });
      void qc.invalidateQueries({ queryKey: promptKeys.detail(id) });
    },
  });
}

export function useCompareVersions(id: string, from: number | null, to: number | null) {
  return useQuery({
    queryKey: ["prompts", "compare", id, from, to],
    queryFn: () => promptsApi.compareVersions(id, from!, to!),
    enabled: Boolean(id) && from != null && to != null && from !== to,
  });
}
