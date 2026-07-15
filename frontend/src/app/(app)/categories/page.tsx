"use client";

import { ChevronRight, FolderTree } from "lucide-react";
import Link from "next/link";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCategoryTree } from "@/hooks/use-taxonomy";
import { cn } from "@/lib/utils";
import type { CategoryNode } from "@/types";

function TreeNode({ node, depth }: { node: CategoryNode; depth: number }) {
  return (
    <div>
      <Link
        href={`/prompts?category_id=${node.id}`}
        className={cn(
          "group flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent",
        )}
        style={{ paddingLeft: `${depth * 1.25 + 0.75}rem` }}
      >
        <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-medium group-hover:text-primary">{node.name}</span>
        {node.description && (
          <span className="truncate text-xs text-muted-foreground">
            — {node.description}
          </span>
        )}
      </Link>
      {node.children?.map((child) => (
        <TreeNode key={child.id} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function CategoriesPage() {
  const { data: tree, isLoading } = useCategoryTree();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Categories</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse prompts by area. Selecting a category includes everything nested
          beneath it.
        </p>
      </div>

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
                <TreeNode key={node.id} node={node} depth={0} />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-14 text-center">
              <FolderTree className="h-10 w-10 text-muted-foreground/40" />
              <p className="mt-3 font-medium">No categories yet</p>
              <p className="mt-1 text-sm text-muted-foreground">
                A moderator can create categories to organize the library.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
