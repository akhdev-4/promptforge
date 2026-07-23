"use client";

import { Loader2, MessageSquare, Send, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useAddComment, useComments, useDeleteComment } from "@/hooks/use-community";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import type { Comment } from "@/types";

function initials(c: Comment["author"]): string {
  const base = (c.full_name?.trim() || c.username?.trim() || "?").split(/\s+/);
  return (base[0]![0]! + (base[1]?.[0] ?? "")).toUpperCase();
}

export function Comments({ promptId }: { promptId: string }) {
  const user = useAuthStore((s) => s.user);
  const { data: comments, isLoading } = useComments(promptId);
  const add = useAddComment(promptId);
  const del = useDeleteComment(promptId);
  const [body, setBody] = React.useState("");
  const canModerate = user?.role === "moderator" || user?.role === "administrator";

  const submit = async () => {
    if (!body.trim() || add.isPending) return;
    await add.mutateAsync(body.trim());
    setBody("");
  };

  return (
    <div className="space-y-4 rounded-xl border border-border p-5">
      <h3 className="flex items-center gap-2 text-sm font-semibold">
        <MessageSquare className="h-4 w-4 text-primary" /> Discussion
        {comments && comments.length > 0 && (
          <span className="text-muted-foreground">({comments.length})</span>
        )}
      </h3>

      {user ? (
        <div className="space-y-2">
          <Textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Share how you used this prompt, tips, or feedback…"
            rows={3}
          />
          <div className="flex justify-end">
            <Button size="sm" onClick={submit} disabled={!body.trim() || add.isPending}>
              {add.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Comment
            </Button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Sign in to join the discussion.</p>
      )}

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : comments && comments.length > 0 ? (
        <ul className="space-y-4">
          {comments.map((c) => (
            <li key={c.id} className="flex gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-xs font-semibold text-primary">
                {c.author.avatar_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={c.author.avatar_url} alt="" className="h-full w-full object-cover" />
                ) : (
                  initials(c.author)
                )}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {c.author.full_name ?? c.author.username ?? "User"}
                  </span>
                  <span className="text-xs text-muted-foreground">{formatDate(c.created_at)}</span>
                  {(user?.id === c.author.id || canModerate) && (
                    <button
                      onClick={() => del.mutate(c.id)}
                      className="ml-auto text-muted-foreground hover:text-destructive"
                      aria-label="Delete comment"
                      title="Delete comment"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
                <p className="whitespace-pre-wrap text-sm text-foreground">{c.body}</p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground">No comments yet — be the first.</p>
      )}
    </div>
  );
}
