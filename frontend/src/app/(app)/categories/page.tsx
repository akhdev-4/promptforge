"use client";

import { ChevronRight, FolderTree, Loader2, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateCategory,
  useDeleteCategory,
  useCategoryTree,
} from "@/hooks/use-taxonomy";
import { ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import type { CategoryNode } from "@/types";

/** Flatten the tree into indented options for the parent selector. */
function flatten(nodes: CategoryNode[], depth = 0): { id: string; label: string }[] {
  return nodes.flatMap((n) => [
    { id: n.id, label: `${"— ".repeat(depth)}${n.name}` },
    ...flatten(n.children ?? [], depth + 1),
  ]);
}

function TreeNode({
  node,
  depth,
  canManage,
  onDelete,
  deletingId,
}: {
  node: CategoryNode;
  depth: number;
  canManage: boolean;
  onDelete: (node: CategoryNode) => void;
  deletingId: string | null;
}) {
  return (
    <div>
      <div
        className="group flex items-center gap-1 rounded-lg pr-2 transition-colors hover:bg-accent"
        style={{ paddingLeft: `${depth * 1.25 + 0.25}rem` }}
      >
        <Link
          href={`/prompts?category_id=${node.id}`}
          className="flex flex-1 items-center gap-2 px-2 py-2 text-sm"
        >
          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
          <span className="font-medium group-hover:text-primary">{node.name}</span>
          {node.description && (
            <span className="truncate text-xs text-muted-foreground">— {node.description}</span>
          )}
        </Link>
        {canManage && (
          <button
            onClick={() => onDelete(node)}
            disabled={deletingId === node.id}
            className="rounded-md p-1.5 text-muted-foreground opacity-0 transition-opacity hover:text-destructive group-hover:opacity-100"
            aria-label={`Delete ${node.name}`}
            title="Delete (removes its subcategories too)"
          >
            {deletingId === node.id ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </button>
        )}
      </div>
      {node.children?.map((child) => (
        <TreeNode
          key={child.id}
          node={child}
          depth={depth + 1}
          canManage={canManage}
          onDelete={onDelete}
          deletingId={deletingId}
        />
      ))}
    </div>
  );
}

export default function CategoriesPage() {
  const { data: tree, isLoading } = useCategoryTree();
  const user = useAuthStore((s) => s.user);
  const canManage = user?.role === "moderator" || user?.role === "administrator";

  const create = useCreateCategory();
  const del = useDeleteCategory();
  const [name, setName] = React.useState("");
  const [parentId, setParentId] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [deletingId, setDeletingId] = React.useState<string | null>(null);

  const parentOptions = React.useMemo(() => flatten(tree ?? []), [tree]);

  const onCreate = async () => {
    if (!name.trim()) return;
    setError(null);
    try {
      await create.mutateAsync({ name: name.trim(), parent_id: parentId || null });
      setName("");
      setParentId("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create category.");
    }
  };

  const onDelete = async (node: CategoryNode) => {
    const kids = node.children?.length
      ? ` and its ${node.children.length} subcategor${node.children.length === 1 ? "y" : "ies"}`
      : "";
    if (!window.confirm(`Delete “${node.name}”${kids}? Prompts stay, but lose this category.`))
      return;
    setDeletingId(node.id);
    try {
      await del.mutateAsync(node.id);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Categories</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse prompts by area. Selecting a category includes everything nested beneath it.
        </p>
      </div>

      {/* Moderator/admin: create form */}
      {canManage && (
        <Card>
          <CardContent className="p-4">
            <p className="mb-3 text-sm font-medium">New category</p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && onCreate()}
                placeholder="Category name (e.g. Landing Pages)"
                className="flex-1"
              />
              <div className="sm:w-56">
                <Select value={parentId} onChange={(e) => setParentId(e.target.value)}>
                  <option value="">Top level (no parent)</option>
                  {parentOptions.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.label}
                    </option>
                  ))}
                </Select>
              </div>
              <Button onClick={onCreate} disabled={create.isPending || !name.trim()}>
                {create.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                Create
              </Button>
            </div>
            {error && <p className="mt-2 text-xs text-destructive">{error}</p>}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="p-3">
          {isLoading ? (
            <div className="space-y-2 p-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-9 w-full" />
              ))}
            </div>
          ) : tree && tree.length > 0 ? (
            <div className="space-y-0.5">
              {tree.map((node) => (
                <TreeNode
                  key={node.id}
                  node={node}
                  depth={0}
                  canManage={canManage}
                  onDelete={onDelete}
                  deletingId={deletingId}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-14 text-center">
              <FolderTree className="h-10 w-10 text-muted-foreground/40" />
              <p className="mt-3 font-medium">No categories yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {canManage
                  ? "Use the form above to create your first category."
                  : "A moderator can create categories to organize the library."}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
