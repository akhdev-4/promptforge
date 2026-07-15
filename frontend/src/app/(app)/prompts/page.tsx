"use client";

import { Library, Plus, Search } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import * as React from "react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { usePrompts } from "@/hooks/use-prompts";
import { useCategoryTree, usePopularTags } from "@/hooks/use-taxonomy";
import { promptTypeOptions, sortOptions } from "@/lib/prompt-meta";
import { cn } from "@/lib/utils";
import type { CategoryNode, PromptSort, PromptType } from "@/types";

const PAGE_SIZE = 12;

function flatten(nodes: CategoryNode[], depth = 0): { id: string; label: string }[] {
  return nodes.flatMap((n) => [
    { id: n.id, label: `${"— ".repeat(depth)}${n.name}` },
    ...flatten(n.children ?? [], depth + 1),
  ]);
}

export default function PromptsPage() {
  return (
    <React.Suspense fallback={null}>
      <PromptsLibrary />
    </React.Suspense>
  );
}

function PromptsLibrary() {
  const searchParams = useSearchParams();
  const [q, setQ] = React.useState("");
  const [debouncedQ, setDebouncedQ] = React.useState("");
  const [type, setType] = React.useState<PromptType | "">("");
  const [categoryId, setCategoryId] = React.useState(
    () => searchParams.get("category_id") ?? "",
  );
  const componentId = searchParams.get("component_id") ?? "";
  const [activeTags, setActiveTags] = React.useState<string[]>([]);
  const [sort, setSort] = React.useState<PromptSort>("newest");
  const [page, setPage] = React.useState(1);

  const { data: tree } = useCategoryTree();
  const { data: popularTags } = usePopularTags(20);
  const categoryOptions = React.useMemo(() => flatten(tree ?? []), [tree]);

  // Debounce the search input.
  React.useEffect(() => {
    const t = setTimeout(() => {
      setDebouncedQ(q);
      setPage(1);
    }, 350);
    return () => clearTimeout(t);
  }, [q]);

  const toggleTag = (slug: string) => {
    setPage(1);
    setActiveTags((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    );
  };

  const { data, isLoading, isError } = usePrompts({
    page,
    size: PAGE_SIZE,
    q: debouncedQ || undefined,
    prompt_type: type || undefined,
    category_id: categoryId || undefined,
    component_id: componentId || undefined,
    tags: activeTags.length ? activeTags : undefined,
    sort,
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Prompt Library</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Browse and reuse production-tested prompts.
          </p>
        </div>
        <Button asChild>
          <Link href="/prompts/new">
            <Plus className="h-4 w-4" />
            New Prompt
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search prompts…"
            className="pl-9"
          />
        </div>
        <div className="w-full sm:w-44">
          <Select
            value={type}
            onChange={(e) => {
              setType(e.target.value as PromptType | "");
              setPage(1);
            }}
          >
            <option value="">All types</option>
            {promptTypeOptions.map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </Select>
        </div>
        <div className="w-full sm:w-52">
          <Select
            value={categoryId}
            onChange={(e) => {
              setCategoryId(e.target.value);
              setPage(1);
            }}
          >
            <option value="">All categories</option>
            {categoryOptions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.label}
              </option>
            ))}
          </Select>
        </div>
        <div className="w-full sm:w-44">
          <Select value={sort} onChange={(e) => setSort(e.target.value as PromptSort)}>
            {sortOptions.map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {/* Popular tag filters */}
      {popularTags && popularTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {popularTags.map((t) => {
            const active = activeTags.includes(t.slug);
            return (
              <button
                key={t.id}
                onClick={() => toggleTag(t.slug)}
                className={cn(
                  "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                  active
                    ? "border-primary/40 bg-primary/10 text-primary"
                    : "border-border text-muted-foreground hover:border-primary/30 hover:text-foreground",
                )}
              >
                #{t.slug}
                <span className="ml-1 opacity-60">{t.usage_count}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Results */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-52 w-full rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <p className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Failed to load prompts. Is the backend running?
        </p>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((p) => (
              <PromptCard key={p.id} prompt={p} />
            ))}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between pt-2">
            <p className="text-sm text-muted-foreground">
              {data.total} prompt{data.total === 1 ? "" : "s"} · page {data.page} of{" "}
              {data.pages || 1}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= (data.pages || 1)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Library className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No prompts found</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {debouncedQ || type
              ? "Try adjusting your filters."
              : "Be the first to add a production-tested prompt."}
          </p>
          <Button asChild className="mt-4">
            <Link href="/prompts/new">
              <Plus className="h-4 w-4" />
              New Prompt
            </Link>
          </Button>
        </div>
      )}
    </div>
  );
}
