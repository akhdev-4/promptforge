/** Playground (prompt runner) API. */

import { apiFetch } from "@/lib/api";
import type { PlaygroundRunResult } from "@/types";

export const playgroundApi = {
  run: (promptId: string, variables: Record<string, string>) =>
    apiFetch<PlaygroundRunResult>(`/prompts/${promptId}/run`, {
      method: "POST",
      body: { variables },
    }),
};
