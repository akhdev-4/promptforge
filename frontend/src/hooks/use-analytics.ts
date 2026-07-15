/** TanStack Query hooks for analytics. */

import { useQuery } from "@tanstack/react-query";

import { analyticsApi } from "@/lib/analytics-api";

export function useOverview() {
  return useQuery({ queryKey: ["analytics", "overview"], queryFn: () => analyticsApi.overview() });
}
export function useTrending(limit = 6) {
  return useQuery({
    queryKey: ["analytics", "trending", limit],
    queryFn: () => analyticsApi.trending(limit),
  });
}
export function useContributors(limit = 5) {
  return useQuery({
    queryKey: ["analytics", "contributors", limit],
    queryFn: () => analyticsApi.contributors(limit),
  });
}
export function useGrowth(days = 30) {
  return useQuery({
    queryKey: ["analytics", "growth", days],
    queryFn: () => analyticsApi.growth(days),
  });
}
export function useByType() {
  return useQuery({ queryKey: ["analytics", "by-type"], queryFn: () => analyticsApi.byType() });
}
