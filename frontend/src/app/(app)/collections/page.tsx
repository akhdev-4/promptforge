"use client";

import { BookMarked, Globe, Loader2, Lock, Plus } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useCreateCollection,
  useMyCollections,
  usePublicCollections,
} from "@/hooks/use-collections";
import type { Collection } from "@/types";
import { useAuthStore } from "@/stores/auth";

function CollectionCard({ c }: { c: Collection }) {
  return (
    <Link href={`/collections/${c.id}`}>
      <Card className="h-full p-5 transition-all hover:border-primary/40 hover:shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <BookMarked className="h-5 w-5" />
          </div>
          {c.is_public ? (
            <Globe className="h-4 w-4 text-muted-foreground" />
          ) : (
            <Lock className="h-4 w-4 text-muted-foreground" />
          )}
        </div>
        <h3 className="mt-3 font-semibold">{c.name}</h3>
        <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
          {c.description ?? "No description."}
        </p>
        <div className="mt-3 flex items-center gap-2">
          <Badge variant="secondary">{c.item_count} prompts</Badge>
          <span className="text-xs text-muted-foreground">
            by {c.author.full_name ?? c.author.username ?? "unknown"}
          </span>
        </div>
      </Card>
    </Link>
  );
}

export default function CollectionsPage() {
  const user = useAuthStore((s) => s.user);
  const { data: publicColls, isLoading } = usePublicCollections();
  const { data: mine } = useMyCollections(Boolean(user));
  const create = useCreateCollection();
  const [name, setName] = React.useState("");

  const onCreate = async () => {
    if (!name.trim()) return;
    await create.mutateAsync({ name: name.trim() });
    setName("");
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Collections</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Curated sets of prompts — share the best of your library.
        </p>
      </div>

      {user && (
        <div className="flex gap-2">
          <Input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && onCreate()}
            placeholder="New collection (e.g. Beautiful Login Pages)"
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

      {user && mine && mine.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Your collections
          </h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {mine.map((c) => (
              <CollectionCard key={c.id} c={c} />
            ))}
          </div>
        </section>
      )}

      <section className="space-y-3">
        <h2 className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
          Public collections
        </h2>
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-40 w-full rounded-xl" />
            ))}
          </div>
        ) : publicColls && publicColls.items.length > 0 ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {publicColls.items.map((c) => (
              <CollectionCard key={c.id} c={c} />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
            <BookMarked className="h-10 w-10 text-muted-foreground/40" />
            <p className="mt-3 font-medium">No public collections yet</p>
          </div>
        )}
      </section>
    </div>
  );
}
