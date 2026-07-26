"use client";

import { FolderKanban, Loader2, Package, Plus } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { useCreateProject, useProjects, useStarterKits } from "@/hooks/use-projects";
import { cn } from "@/lib/utils";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export default function ProjectsPage() {
  const { data, isLoading } = useProjects();
  const { data: kits } = useStarterKits();
  const create = useCreateProject();
  const user = useAuthStore((s) => s.user);
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [filter, setFilter] = React.useState<"all" | "codebase">("all");

  const codebaseIds = React.useMemo(
    () => new Set((kits?.items ?? []).map((k) => k.project_id)),
    [kits],
  );

  const onCreate = async () => {
    if (!name.trim()) return;
    await create.mutateAsync({
      name: name.trim(),
      description: description.trim() || undefined,
    });
    setName("");
    setDescription("");
  };

  const allItems = data?.items ?? [];
  const items =
    filter === "codebase" ? allItems.filter((p) => codebaseIds.has(p.id)) : allItems;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Projects</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Assemble applications from proven prompt modules — organize prompts into
          Application → Module → Component.
        </p>
      </div>

      {user && (
        <div className="max-w-xl space-y-2 rounded-xl border border-border p-4">
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onCreate()}
            placeholder="New project name (e.g. CRM Application)"
          />
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Description (optional) — what is this application?"
            className="min-h-16"
            maxLength={1000}
          />
          <div className="flex justify-end">
            <Button onClick={onCreate} disabled={create.isPending || !name.trim()}>
              {create.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Create project
            </Button>
          </div>
        </div>
      )}

      {allItems.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {(["all", "codebase"] as const).map((value) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={cn(
                "rounded-full border px-3 py-1 text-sm transition-colors",
                filter === value
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              {value === "all" ? "All projects" : "With codebase"}
              {value === "codebase" && codebaseIds.size > 0 && (
                <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-xs">
                  {codebaseIds.size}
                </span>
              )}
            </button>
          ))}
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))}
        </div>
      ) : allItems.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <FolderKanban className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No projects yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first application to start organizing prompts.
          </p>
        </div>
      ) : items.length === 0 ? (
        <p className="rounded-xl border border-dashed border-border py-12 text-center text-sm text-muted-foreground">
          No projects with a codebase yet. Attach one from a project&rsquo;s{" "}
          <span className="font-medium">Codebase</span> tab.
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card className="h-full p-5 transition-all hover:border-primary/40 hover:shadow-md">
                <div className="flex items-start justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <FolderKanban className="h-5 w-5" />
                  </div>
                  {codebaseIds.has(p.id) && (
                    <Badge variant="secondary" className="gap-1">
                      <Package className="h-3 w-3" /> Codebase
                    </Badge>
                  )}
                </div>
                <h3 className="mt-3 font-semibold group-hover:text-primary">{p.name}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                  {p.description ?? "No description."}
                </p>
                <p className="mt-3 text-xs text-muted-foreground">
                  by {p.author.full_name ?? p.author.username ?? "unknown"} ·{" "}
                  {formatDate(p.created_at)}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
