"use client";

import { Code2, LayoutGrid, Library, Plus, Search, Wand2 } from "lucide-react";
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

const CREATIVE_ROOT = "Creative & Media";

type Lane = "all" | "dev" | "creative";

const LANES: { value: Lane; label: string; icon: typeof Code2; hint: string }[] = [
  { value: "all", label: "All prompts", icon: LayoutGrid, hint: "Everything in the library" },
  {
    value: "dev",
    label: "App Development",
    icon: Code2,
    hint: "Code, UI, APIs, databases & DevOps",
  },
  {
    value: "creative",
    label: "AI & Creative",
    icon: Wand2,
    hint: "AI image generation & photo editing",
  },
];

// Per-lane color + decorative art for the (catchy) lane cards.
function CloudsArt() {
  return (
    <svg
      viewBox="0 0 140 70"
      className="pointer-events-none absolute right-1 top-1/2 h-full w-32 -translate-y-1/2 text-violet-400/25"
      fill="currentColor"
      aria-hidden
    >
      <ellipse cx="96" cy="50" rx="34" ry="15" />
      <ellipse cx="66" cy="55" rx="22" ry="11" />
      <circle cx="112" cy="20" r="3" />
      <circle cx="90" cy="14" r="2" />
      <circle cx="122" cy="34" r="2" />
      <path d="M104 8l1.6 3.2 3.4.5-2.5 2.4.6 3.4-3.1-1.6-3 1.6.6-3.4-2.5-2.4 3.4-.5z" />
    </svg>
  );
}
function CodeArt() {
  return (
    <div
      className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 select-none text-right font-mono text-[10px] leading-[13px] text-sky-500/25"
      aria-hidden
    >
      <div>1010&nbsp;0110</div>
      <div>0110&nbsp;1011</div>
      <div>1101&nbsp;0010</div>
      <Code2 className="ml-auto mt-0.5 h-7 w-7 text-sky-500/30" />
    </div>
  );
}
function CreativeArt() {
  return (
    <svg
      viewBox="0 0 110 66"
      className="pointer-events-none absolute right-2 top-1/2 h-full w-28 -translate-y-1/2 text-pink-400/30"
      aria-hidden
    >
      <g stroke="currentColor" strokeWidth="1.3" fill="none">
        <line x1="22" y1="22" x2="52" y2="12" />
        <line x1="22" y1="22" x2="46" y2="44" />
        <line x1="52" y1="12" x2="84" y2="28" />
        <line x1="46" y1="44" x2="84" y2="28" />
        <line x1="46" y1="44" x2="72" y2="54" />
      </g>
      <g fill="currentColor">
        <circle cx="22" cy="22" r="4" />
        <circle cx="52" cy="12" r="4" />
        <circle cx="46" cy="44" r="4" />
        <circle cx="72" cy="54" r="3" />
      </g>
      <circle cx="84" cy="28" r="5" className="fill-fuchsia-400/50" />
    </svg>
  );
}

const LANE_STYLES: Record<
  Lane,
  { gradient: string; ring: string; tile: string; art: React.ReactNode }
> = {
  all: {
    gradient: "from-violet-500/20 via-purple-400/10 to-fuchsia-300/5",
    ring: "ring-violet-400",
    tile: "bg-violet-500/20 text-violet-600 dark:text-violet-300",
    art: <CloudsArt />,
  },
  dev: {
    gradient: "from-sky-500/20 via-blue-400/10 to-cyan-300/5",
    ring: "ring-sky-400",
    tile: "bg-sky-500/20 text-sky-600 dark:text-sky-300",
    art: <CodeArt />,
  },
  creative: {
    gradient: "from-pink-500/20 via-rose-400/10 to-fuchsia-300/5",
    ring: "ring-pink-400",
    tile: "bg-pink-500/20 text-pink-600 dark:text-pink-300",
    art: <CreativeArt />,
  },
};

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
  const [lane, setLane] = React.useState<Lane>("all");
  const [activeTags, setActiveTags] = React.useState<string[]>([]);
  const [sort, setSort] = React.useState<PromptSort>("newest");
  const [page, setPage] = React.useState(1);

  const { data: tree } = useCategoryTree();
  const { data: popularTags } = usePopularTags(20);

  // Split the category tree into the "Creative & Media" subtree vs. everything
  // else, so each lane scopes its category dropdown and its query.
  const creativeRoot = React.useMemo(
    () => (tree ?? []).find((n) => n.name === CREATIVE_ROOT),
    [tree],
  );
  const creativeRootId = creativeRoot?.id;
  const creativeOptions = React.useMemo(
    () => flatten(creativeRoot?.children ?? []),
    [creativeRoot],
  );
  const devOptions = React.useMemo(
    () => flatten((tree ?? []).filter((n) => n.id !== creativeRootId)),
    [tree, creativeRootId],
  );
  const allOptions = React.useMemo(() => flatten(tree ?? []), [tree]);
  const categoryOptions =
    lane === "creative" ? creativeOptions : lane === "dev" ? devOptions : allOptions;

  const changeLane = (next: Lane) => {
    setLane(next);
    setCategoryId(""); // clear any drill-down that belonged to the old lane
    setPage(1);
  };

  // An explicit category drill-down wins; otherwise the lane sets the scope.
  const categoryFilter = categoryId
    ? { category_id: categoryId }
    : lane === "creative" && creativeRootId
      ? { category_id: creativeRootId }
      : lane === "dev" && creativeRootId
        ? { exclude_category_id: creativeRootId }
        : {};

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
    ...categoryFilter,
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
            Pick a lane below — app development or AI &amp; creative — then search and filter.
          </p>
        </div>
        <Button asChild>
          <Link href="/prompts/new">
            <Plus className="h-4 w-4" />
            New Prompt
          </Link>
        </Button>
      </div>

      {/* Lane switcher: App Development vs AI & Creative */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {LANES.map((l) => {
          const active = lane === l.value;
          const Icon = l.icon;
          const s = LANE_STYLES[l.value];
          return (
            <button
              key={l.value}
              onClick={() => changeLane(l.value)}
              aria-pressed={active}
              className={cn(
                "group relative flex min-h-[76px] items-center gap-3 overflow-hidden rounded-2xl border bg-gradient-to-r p-4 text-left transition-all",
                s.gradient,
                active
                  ? cn("border-transparent shadow-md ring-2", s.ring)
                  : "border-border hover:shadow-sm hover:brightness-[1.02]",
              )}
            >
              {s.art}
              <span
                className={cn(
                  "relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-sm",
                  s.tile,
                )}
              >
                <Icon className="h-5 w-5" />
              </span>
              <span className="relative min-w-0">
                <span className="block text-sm font-semibold text-foreground">{l.label}</span>
                <span className="block truncate text-xs text-muted-foreground">{l.hint}</span>
              </span>
            </button>
          );
        })}
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
