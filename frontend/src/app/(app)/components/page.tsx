"use client";

import { Blocks, Boxes, FolderKanban, Layers, Plus, Search } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useComponents } from "@/hooks/use-projects";
import { useAuthStore } from "@/stores/auth";

export default function ComponentsPage() {
  const { data, isLoading } = useComponents();
  const user = useAuthStore((s) => s.user);
  const [q, setQ] = React.useState("");

  const items = data?.items ?? [];
  const filtered = React.useMemo(() => {
    const term = q.trim().toLowerCase();
    if (!term) return items;
    return items.filter((c) =>
      [c.name, c.module_name, c.project_name, c.description ?? ""]
        .join(" ")
        .toLowerCase()
        .includes(term),
    );
  }, [items, q]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Components</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Reusable building blocks across every project. Each component (e.g. Login, Navbar,
          Pricing Table) collects proven prompt variants you can drop into an application.
        </p>
      </div>

      {items.length > 0 && (
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search components, modules, projects…"
            className="pl-9"
          />
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-40 w-full rounded-xl" />
          ))}
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((c) => (
            <Card key={c.id} className="flex h-full flex-col p-5">
              <div className="flex items-start justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Boxes className="h-5 w-5" />
                </div>
                <Badge variant="secondary">
                  {c.prompt_count} {c.prompt_count === 1 ? "variant" : "variants"}
                </Badge>
              </div>

              <h3 className="mt-3 font-semibold">{c.name}</h3>
              {c.description && (
                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{c.description}</p>
              )}

              <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
                <Link
                  href={`/projects/${c.project_id}`}
                  className="inline-flex items-center gap-1 hover:text-foreground"
                >
                  <FolderKanban className="h-3.5 w-3.5" /> {c.project_name}
                </Link>
                <span className="inline-flex items-center gap-1">
                  <Layers className="h-3.5 w-3.5" /> {c.module_name}
                </span>
              </div>

              <div className="mt-4 flex gap-2 border-t border-border pt-3">
                <Button variant="outline" size="sm" asChild className="flex-1">
                  <Link href={`/prompts?component_id=${c.id}`}>View variants</Link>
                </Button>
                {user && (
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/prompts/new?component_id=${c.id}`}>
                      <Plus className="h-4 w-4" /> Variant
                    </Link>
                  </Button>
                )}
              </div>
            </Card>
          ))}
        </div>
      ) : items.length > 0 ? (
        <p className="text-sm text-muted-foreground">No components match “{q}”.</p>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Blocks className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No components yet</p>
          <p className="mt-1 max-w-sm text-sm text-muted-foreground">
            Components live inside a project&rsquo;s modules. Open a project, add a module, then
            add components to it.
          </p>
          <Button asChild className="mt-4">
            <Link href="/projects">
              <FolderKanban className="h-4 w-4" /> Go to projects
            </Link>
          </Button>
        </div>
      )}
    </div>
  );
}
