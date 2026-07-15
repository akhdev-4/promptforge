"use client";

import { Bookmark } from "lucide-react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Skeleton } from "@/components/ui/skeleton";
import { useMyBookmarks } from "@/hooks/use-collections";

export default function FavoritesPage() {
  const { data, isLoading } = useMyBookmarks();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Favorites</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Prompts you&apos;ve bookmarked for quick access.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-52 w-full rounded-xl" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((p) => (
            <PromptCard key={p.id} prompt={p} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Bookmark className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No favorites yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Bookmark prompts with the “Save” button to find them here.
          </p>
        </div>
      )}
    </div>
  );
}
