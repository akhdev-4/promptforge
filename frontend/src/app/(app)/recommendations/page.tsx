"use client";

import { Sparkles } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useRecommendations } from "@/hooks/use-recommendations";
import type { RecommendationItem } from "@/types";

/** Group recommendations by their reason, preserving first-seen order. */
function groupByReason(items: RecommendationItem[]): [string, RecommendationItem[]][] {
  const groups = new Map<string, RecommendationItem[]>();
  for (const item of items) {
    const bucket = groups.get(item.reason) ?? [];
    bucket.push(item);
    groups.set(item.reason, bucket);
  }
  return [...groups.entries()];
}

export default function RecommendationsPage() {
  const { data, isLoading } = useRecommendations();
  const groups = React.useMemo(() => groupByReason(data ?? []), [data]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Sparkles className="h-6 w-6 text-primary" /> Recommended for you
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Prompts picked from what you&rsquo;ve bookmarked — similar tags, components, and
          categories — topped up with what&rsquo;s trending across PromptForge.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-52 w-full rounded-xl" />
          ))}
        </div>
      ) : groups.length > 0 ? (
        <div className="space-y-8">
          {groups.map(([reason, items]) => (
            <section key={reason} className="space-y-3">
              <h2 className="text-sm font-medium text-muted-foreground">{reason}</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {items.map((item) => (
                  <PromptCard key={item.prompt.id} prompt={item.prompt} />
                ))}
              </div>
            </section>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Sparkles className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">Nothing to recommend yet</p>
          <p className="mt-1 max-w-sm text-sm text-muted-foreground">
            Bookmark a few prompts you like and we&rsquo;ll tailor this feed to you. In the
            meantime, explore the library to get started.
          </p>
          <Button asChild className="mt-4">
            <Link href="/prompts">Browse prompts</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
