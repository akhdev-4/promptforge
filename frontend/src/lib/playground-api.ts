/** Playground (prompt runner) API. */

import { apiFetch } from "@/lib/api";
import { apiUrl } from "@/lib/config";
import { tokenStore } from "@/lib/token-store";
import type { PlaygroundRunResult } from "@/types";

export type RunMode = "text" | "image";

export const playgroundApi = {
  run: (promptId: string, variables: Record<string, string>, mode: RunMode = "text") =>
    apiFetch<PlaygroundRunResult>(`/prompts/${promptId}/run`, {
      method: "POST",
      body: { variables, mode },
    }),
};

/** Stream a text run, invoking `onChunk` with each delta as it arrives. */
export async function streamRun(
  promptId: string,
  variables: Record<string, string>,
  onChunk: (text: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const token = tokenStore.getAccess();
  const res = await fetch(apiUrl(`/prompts/${promptId}/run/stream`), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ variables, mode: "text" }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`Run failed (${res.status})`);
  }
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(decoder.decode(value, { stream: true }));
  }
}
