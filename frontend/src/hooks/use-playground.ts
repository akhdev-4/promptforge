/** Playground run hook. */

import { useMutation } from "@tanstack/react-query";

import { playgroundApi } from "@/lib/playground-api";

export function useRunPrompt(promptId: string) {
  return useMutation({
    mutationFn: (variables: Record<string, string>) =>
      playgroundApi.run(promptId, variables),
  });
}
