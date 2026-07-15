"use client";

import { ArrowLeft, Boxes, Layers, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAddComponent,
  useAddModule,
  useDeleteProject,
  useProjectTree,
} from "@/hooks/use-projects";
import { useAuthStore } from "@/stores/auth";

function InlineAdd({
  placeholder,
  onAdd,
}: {
  placeholder: string;
  onAdd: (name: string) => void;
}) {
  const [name, setName] = React.useState("");
  const submit = () => {
    if (name.trim()) {
      onAdd(name.trim());
      setName("");
    }
  };
  return (
    <div className="flex gap-2">
      <Input
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder={placeholder}
        className="h-9 max-w-xs"
      />
      <Button size="sm" variant="outline" onClick={submit} disabled={!name.trim()}>
        <Plus className="h-4 w-4" /> Add
      </Button>
    </div>
  );
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const { data: tree, isLoading } = useProjectTree(id);
  const addModule = useAddModule(id);
  const addComponent = useAddComponent(id);
  const del = useDeleteProject();

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  if (!tree) {
    return <div className="text-sm text-destructive">Project not found.</div>;
  }

  const canManage =
    user?.id === tree.author.id ||
    user?.role === "moderator" ||
    user?.role === "administrator";

  const onDelete = async () => {
    if (!window.confirm("Delete this project and all its modules/components?")) return;
    await del.mutateAsync(tree.id);
    router.push("/projects");
  };

  return (
    <div className="space-y-6">
      <Link
        href="/projects"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> Back to projects
      </Link>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">{tree.name}</h1>
          {tree.description && (
            <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{tree.description}</p>
          )}
          <p className="mt-2 text-xs text-muted-foreground">
            by {tree.author.full_name ?? tree.author.username ?? "unknown"} ·{" "}
            {tree.modules.length} module{tree.modules.length === 1 ? "" : "s"}
          </p>
        </div>
        {canManage && (
          <Button variant="destructive" onClick={onDelete} disabled={del.isPending}>
            <Trash2 className="h-4 w-4" /> Delete project
          </Button>
        )}
      </div>

      <div className="space-y-4">
        {tree.modules.map((module) => (
          <Card key={module.id}>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-primary" /> {module.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {module.components.length > 0 ? (
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {module.components.map((comp) => (
                    <div
                      key={comp.id}
                      className="flex items-center justify-between rounded-lg border border-border px-3 py-2"
                    >
                      <div className="flex items-center gap-2">
                        <Boxes className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{comp.name}</span>
                        <Badge variant="secondary">{comp.prompt_count}</Badge>
                      </div>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/prompts?component_id=${comp.id}`}>Variants</Link>
                        </Button>
                        {user && (
                          <Button variant="ghost" size="sm" asChild>
                            <Link href={`/prompts/new?component_id=${comp.id}`}>
                              <Plus className="h-3.5 w-3.5" />
                            </Link>
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No components yet.</p>
              )}

              {canManage && (
                <InlineAdd
                  placeholder="Add component (e.g. Login)"
                  onAdd={(name) => addComponent.mutate({ moduleId: module.id, name })}
                />
              )}
            </CardContent>
          </Card>
        ))}

        {tree.modules.length === 0 && (
          <p className="text-sm text-muted-foreground">
            No modules yet. {canManage ? "Add one below." : ""}
          </p>
        )}

        {canManage && (
          <Card className="border-dashed">
            <CardContent className="p-4">
              <p className="mb-2 text-sm font-medium">Add a module</p>
              <InlineAdd
                placeholder="Module name (e.g. Authentication)"
                onAdd={(name) => addModule.mutate({ name })}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
