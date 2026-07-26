"use client";

import { useQuery } from "@tanstack/react-query";
import { Boxes, ChevronRight, Plus } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { CopyButton } from "@/components/prompts/copy-button";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { promptKeys, usePrompts } from "@/hooks/use-prompts";
import { promptsApi } from "@/lib/prompts-api";
import { cn } from "@/lib/utils";

/** A single prompt variant: expand to view its content and copy it inline. */
function VariantRow({ promptId, title }: { promptId: string; title: string }) {
  const [open, setOpen] = React.useState(false);
  const { data: detail, isLoading } = useQuery({
    queryKey: promptKeys.detail(promptId),
    queryFn: () => promptsApi.get(promptId),
    enabled: open, // lazy — only fetch content when expanded
  });

  return (
    <div className="rounded-lg border border-border bg-background">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
      >
        <span className="flex min-w-0 items-center gap-2 text-sm font-medium">
          <ChevronRight
            className={cn(
              "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
              open && "rotate-90",
            )}
          />
          <span className="truncate">{title}</span>
        </span>
        <span className="shrink-0 text-xs text-muted-foreground">{open ? "Hide" : "View"}</span>
      </button>

      {open && (
        <div className="border-t border-border p-3">
          {isLoading || !detail ? (
            <p className="text-sm text-muted-foreground">Loading prompt…</p>
          ) : (
            <>
              <div className="mb-2 flex items-center justify-between gap-2">
                <CopyButton
                  promptId={detail.id}
                  content={detail.content}
                  size="sm"
                  variant="outline"
                />
                <Link
                  href={`/prompts/${detail.id}`}
                  className="text-xs text-primary hover:underline"
                >
                  Open full prompt →
                </Link>
              </div>
              <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-3 text-xs leading-relaxed">
                {detail.content}
              </pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function VariantList({ componentId }: { componentId: string }) {
  const { data, isLoading } = usePrompts({ component_id: componentId, size: 50 });
  const variants = data?.items ?? [];

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading variants…</p>;
  }
  if (variants.length === 0) {
    return <p className="text-sm text-muted-foreground">No prompt variants yet.</p>;
  }
  return (
    <div className="space-y-2">
      {variants.map((v) => (
        <VariantRow key={v.id} promptId={v.id} title={v.title} />
      ))}
    </div>
  );
}

/** A component inside a module: expand to browse its prompt variants inline. */
export function ProjectComponentRow({
  id,
  name,
  promptCount,
  canAddVariant,
}: {
  id: string;
  name: string;
  promptCount: number;
  canAddVariant: boolean;
}) {
  const [open, setOpen] = React.useState(false);

  return (
    <div className="rounded-lg border border-border">
      <div className="flex items-center justify-between gap-2 px-3 py-2">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex min-w-0 items-center gap-2 text-left"
        >
          <ChevronRight
            className={cn(
              "h-4 w-4 shrink-0 text-muted-foreground transition-transform",
              open && "rotate-90",
            )}
          />
          <Boxes className="h-4 w-4 shrink-0 text-muted-foreground" />
          <span className="truncate text-sm font-medium">{name}</span>
          <Badge variant="secondary">{promptCount}</Badge>
        </button>
        <div className="flex shrink-0 gap-1">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/prompts?component_id=${id}`}>Library</Link>
          </Button>
          {canAddVariant && (
            <Button variant="ghost" size="sm" asChild>
              <Link href={`/prompts/new?component_id=${id}`}>
                <Plus className="h-3.5 w-3.5" />
              </Link>
            </Button>
          )}
        </div>
      </div>
      {open && (
        <div className="border-t border-border bg-muted/30 p-3">
          <VariantList componentId={id} />
        </div>
      )}
    </div>
  );
}
