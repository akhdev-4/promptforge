/** Playground run hook. */

import { useMutation } from "@tanstack/react-query";

import { playgroundApi, type RunMode } from "@/lib/playground-api";

export function useRunPrompt(promptId: string) {
  return useMutation({
    mutationFn: (args: { variables: Record<string, string>; mode: RunMode }) =>
      playgroundApi.run(promptId, args.variables, args.mode),
  });
}
