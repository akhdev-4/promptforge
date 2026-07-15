"use client";

import { Check, FolderPlus, Loader2, Plus } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useAddToCollection,
  useCreateCollection,
  useMyCollections,
} from "@/hooks/use-collections";
import { useAuthStore } from "@/stores/auth";

export function AddToCollection({ promptId }: { promptId: string }) {
  const user = useAuthStore((s) => s.user);
  const [open, setOpen] = React.useState(false);
  const [newName, setNewName] = React.useState("");
  const [addedTo, setAddedTo] = React.useState<Set<string>>(new Set());
  const ref = React.useRef<HTMLDivElement>(null);

  const { data: collections } = useMyCollections(open);
  const add = useAddToCollection();
  const create = useCreateCollection();

  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;

  const addTo = async (collectionId: string) => {
    await add.mutateAsync({ collectionId, promptId });
    setAddedTo((prev) => new Set(prev).add(collectionId));
  };

  const createAndAdd = async () => {
    if (!newName.trim()) return;
    const coll = await create.mutateAsync({ name: newName.trim() });
    setNewName("");
    await addTo(coll.id);
  };

  return (
    <div className="relative" ref={ref}>
      <Button variant="outline" onClick={() => setOpen((v) => !v)}>
        <FolderPlus className="h-4 w-4" /> Save to collection
      </Button>
      {open && (
        <div className="absolute right-0 z-50 mt-2 w-72 rounded-xl border border-border bg-popover p-2 shadow-lg">
          <div className="max-h-56 space-y-1 overflow-y-auto">
            {collections && collections.length > 0 ? (
              collections.map((c) => {
                const added = addedTo.has(c.id);
                return (
                  <button
                    key={c.id}
                    onClick={() => addTo(c.id)}
                    disabled={added}
                    className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-accent disabled:opacity-60"
                  >
                    <span className="truncate">{c.name}</span>
                    {added ? (
                      <Check className="h-4 w-4 text-success" />
                    ) : (
                      <Plus className="h-4 w-4 text-muted-foreground" />
                    )}
                  </button>
                );
              })
            ) : (
              <p className="px-3 py-2 text-xs text-muted-foreground">
                No collections yet — create one below.
              </p>
            )}
          </div>
          <div className="mt-2 flex gap-2 border-t border-border pt-2">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && createAndAdd()}
              placeholder="New collection…"
              className="h-9"
            />
            <Button size="sm" onClick={createAndAdd} disabled={create.isPending || !newName.trim()}>
              {create.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Add"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
