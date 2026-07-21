/** Personalized "For You" recommendation feed. */

import { useQuery } from "@tanstack/react-query";

import { authApi } from "@/lib/auth-api";
import { useAuthStore } from "@/stores/auth";

export function useRecommendations(limit = 12) {
  const user = useAuthStore((s) => s.user);
  return useQuery({
    queryKey: ["recommendations", limit],
    queryFn: () => authApi.recommendations(limit),
    enabled: Boolean(user),
  });
}
