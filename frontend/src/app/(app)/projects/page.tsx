"use client";

import { FolderKanban, Loader2, Plus } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateProject, useProjects } from "@/hooks/use-projects";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export default function ProjectsPage() {
  const { data, isLoading } = useProjects();
  const create = useCreateProject();
  const user = useAuthStore((s) => s.user);
  const [name, setName] = React.useState("");

  const onCreate = async () => {
    if (!name.trim()) return;
    await create.mutateAsync({ name: name.trim() });
    setName("");
  };

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
        <div className="flex gap-2">
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onCreate()}
            placeholder="New project name (e.g. CRM Application)"
            className="max-w-sm"
          />
          <Button onClick={onCreate} disabled={create.isPending || !name.trim()}>
            {create.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            Create
          </Button>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {data.items.map((p) => (
            <Link key={p.id} href={`/projects/${p.id}`}>
              <Card className="h-full p-5 transition-all hover:border-primary/40 hover:shadow-md">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <FolderKanban className="h-5 w-5" />
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
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <FolderKanban className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No projects yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Create your first application to start organizing prompts.
          </p>
        </div>
      )}
    </div>
  );
}
