/** Personal API keys (for the public API used by the CLI / IDE plugin). */

import { apiFetch } from "@/lib/api";
import type { ApiKey, ApiKeyCreated } from "@/types";

export const apiKeysApi = {
  list: () => apiFetch<ApiKey[]>("/keys"),
  create: (name: string, write = false) =>
    apiFetch<ApiKeyCreated>("/keys", { method: "POST", body: { name, write } }),
  revoke: (id: string) => apiFetch<void>(`/keys/${id}`, { method: "DELETE" }),
};
