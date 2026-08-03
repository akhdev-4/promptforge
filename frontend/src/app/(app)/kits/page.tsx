"use client";

import { useQuery } from "@tanstack/react-query";
import { Boxes, Download, ExternalLink, Package } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { KIT_CATEGORIES, KIT_CATEGORY_LABEL } from "@/lib/kit-categories";
import { projectsApi } from "@/lib/projects-api";
import { cn } from "@/lib/utils";
import type { KitCategory, KitTemplate } from "@/types";

function KitCard({ kit }: { kit: KitTemplate }) {
  return (
    <Card className="flex flex-col">
      <CardContent className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold leading-tight">{kit.name}</h3>
          {kit.category && (
            <span className="shrink-0 rounded-md bg-primary/10 px-2 py-0.5 text-[11px] font-medium text-primary">
              {KIT_CATEGORY_LABEL[kit.category]}
            </span>
          )}
        </div>
        {kit.description && (
          <p className="line-clamp-2 text-sm text-muted-foreground">{kit.description}</p>
        )}
        {kit.stack && (
          <p className="text-xs text-muted-foreground">
            <span className="font-medium text-foreground">Stack:</span> {kit.stack}
          </p>
        )}
        <div className="mt-auto flex items-center gap-2 pt-1">
          <Badge variant="secondary" className="gap-1">
            <Boxes className="h-3 w-3" /> {kit.prompt_count} prompt
            {kit.prompt_count === 1 ? "" : "s"}
          </Badge>
          {kit.downloads_count > 0 && (
            <Badge variant="secondary" className="gap-1">
              <Download className="h-3 w-3" /> {kit.downloads_count}
            </Badge>
          )}
          <div className="ml-auto flex gap-1.5">
            <Button size="sm" variant="ghost" asChild>
              <Link href={`/projects/${kit.project_id}`}>
                <ExternalLink className="h-3.5 w-3.5" /> View
              </Link>
            </Button>
            <Button size="sm" asChild>
              <a href={projectsApi.templateDownloadUrl(kit.project_id)}>
                <Download className="h-3.5 w-3.5" /> Code
              </a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function KitsPage() {
  const [active, setActive] = React.useState<KitCategory | "all">("all");
  const { data, isLoading } = useQuery({
    queryKey: ["kits"],
    queryFn: () => projectsApi.browseTemplates(),
  });

  const kits = data?.items ?? [];
  const visible = active === "all" ? kits : kits.filter((k) => k.category === active);

  // Categories that actually have kits, in curated order.
  const groups = KIT_CATEGORIES.filter((c) =>
    visible.some((k) => k.category === c.value),
  );
  const uncategorized = visible.filter((k) => !k.category);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Package className="h-6 w-6 text-primary" /> Starter Kits
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Complete initial codebases you can pull and build on — grouped by project type.
          Each kit ships with the proven prompts behind it.
        </p>
      </div>

      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {(["all", ...KIT_CATEGORIES.map((c) => c.value)] as const).map((value) => {
          const label = value === "all" ? "All" : KIT_CATEGORY_LABEL[value];
          return (
            <button
              key={value}
              onClick={() => setActive(value)}
              className={cn(
                "rounded-full border px-3 py-1 text-sm transition-colors",
                active === value
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              {label}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full" />
          ))}
        </div>
      ) : visible.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-10 text-center">
          <p className="text-sm text-muted-foreground">
            No starter kits here yet. Owners can turn a project into a kit from its page —
            open a project and add a <span className="font-medium">Starter template</span>.
          </p>
        </div>
      ) : (
        <div className="space-y-8">
          {groups.map((c) => (
            <section key={c.value} className="space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                {c.label}
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {visible
                  .filter((k) => k.category === c.value)
                  .map((kit) => (
                    <KitCard key={kit.project_id} kit={kit} />
                  ))}
              </div>
            </section>
          ))}
          {uncategorized.length > 0 && (
            <section className="space-y-3">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Uncategorized
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {uncategorized.map((kit) => (
                  <KitCard key={kit.project_id} kit={kit} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
