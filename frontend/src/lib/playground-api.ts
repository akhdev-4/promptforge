/** Playground (prompt runner) API. */

import { apiFetch } from "@/lib/api";
import type { PlaygroundRunResult } from "@/types";

export type RunMode = "text" | "image";

export const playgroundApi = {
  run: (promptId: string, variables: Record<string, string>, mode: RunMode = "text") =>
    apiFetch<PlaygroundRunResult>(`/prompts/${promptId}/run`, {
      method: "POST",
      body: { variables, mode },
    }),
};
