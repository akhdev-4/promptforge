"use client";

import { ArrowLeft, Check, Globe, Link2, Lock, Trash2, X } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCollection,
  useDeleteCollection,
  useRemoveFromCollection,
} from "@/hooks/use-collections";
import { useAuthStore } from "@/stores/auth";

export default function CollectionDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const { data: collection, isLoading, isError } = useCollection(id);
  const del = useDeleteCollection();
  const removeItem = useRemoveFromCollection(id);
  const [copied, setCopied] = React.useState(false);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  if (isError || !collection) {
    return (
      <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
        Collection not found or private.
      </div>
    );
  }

  const isOwner = user?.id === collection.author.id;
  const canManage = isOwner || user?.role === "moderator" || user?.role === "administrator";

  const share = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard unavailable */
    }
  };

  const onDelete = async () => {
    if (!window.confirm("Delete this collection?")) return;
    await del.mutateAsync(collection.id);
    router.push("/collections");
  };

  return (
    <div className="space-y-6">
      <Link
        href="/collections"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> Back to collections
      </Link>

      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-tight">{collection.name}</h1>
            {collection.is_public ? (
              <Badge variant="success">
                <Globe className="mr-1 h-3 w-3" /> Public
              </Badge>
            ) : (
              <Badge variant="warning">
                <Lock className="mr-1 h-3 w-3" /> Private
              </Badge>
            )}
          </div>
          {collection.description && (
            <p className="max-w-2xl text-sm text-muted-foreground">{collection.description}</p>
          )}
          <p className="text-xs text-muted-foreground">
            {collection.item_count} prompt{collection.item_count === 1 ? "" : "s"} · by{" "}
            {collection.author.full_name ?? collection.author.username ?? "unknown"}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={share}>
            {copied ? <Check className="h-4 w-4" /> : <Link2 className="h-4 w-4" />}
            {copied ? "Copied!" : "Share"}
          </Button>
          {canManage && (
            <Button variant="destructive" onClick={onDelete} disabled={del.isPending}>
              <Trash2 className="h-4 w-4" /> Delete
            </Button>
          )}
        </div>
      </div>

      {collection.items.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {collection.items.map((p) => (
            <div key={p.id} className="relative">
              <PromptCard prompt={p} />
              {canManage && (
                <button
                  onClick={() => removeItem.mutate(p.id)}
                  className="absolute right-3 top-3 z-10 rounded-full bg-background/90 p-1 text-muted-foreground shadow hover:text-destructive"
                  aria-label="Remove from collection"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-border py-16 text-center text-sm text-muted-foreground">
          This collection is empty. Add prompts from any prompt page via “Save to
          collection”.
        </div>
      )}
    </div>
  );
}
