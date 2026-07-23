"use client";

import { ArrowLeft, Crown, Loader2, Lock, UserPlus, Users, X } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import { useAddMember, useRemoveMember, useTeam, useTeamPrompts } from "@/hooks/use-teams";

function initials(m: { full_name: string | null; username: string | null }): string {
  const base = (m.full_name?.trim() || m.username?.trim() || "?").split(/\s+/);
  return (base[0]![0]! + (base[1]?.[0] ?? "")).toUpperCase();
}

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: team, isLoading, isError } = useTeam(id);
  const { data: prompts } = useTeamPrompts(id);
  const addMember = useAddMember(id);
  const removeMember = useRemoveMember(id);
  const [username, setUsername] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const onAdd = async () => {
    if (!username.trim()) return;
    setError(null);
    try {
      await addMember.mutateAsync(username.trim().replace(/^@/, ""));
      setUsername("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't add that user.");
    }
  };

  if (isLoading) {
    return <Skeleton className="h-64 w-full rounded-xl" />;
  }
  if (isError || !team) {
    return (
      <p className="text-sm text-muted-foreground">
        You don&rsquo;t have access to this team, or it doesn&rsquo;t exist.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        href="/teams"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> All teams
      </Link>

      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Users className="h-6 w-6 text-primary" /> {team.name}
        </h1>
        {team.description && (
          <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{team.description}</p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Members */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Members ({team.members.length})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {team.is_owner && (
              <div className="space-y-1">
                <div className="flex gap-2">
                  <Input
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && onAdd()}
                    placeholder="@username"
                    className="h-9"
                  />
                  <Button size="sm" onClick={onAdd} disabled={addMember.isPending || !username.trim()}>
                    {addMember.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <UserPlus className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                {error && <p className="text-xs text-destructive">{error}</p>}
              </div>
            )}
            <ul className="space-y-2">
              {team.members.map((m) => (
                <li key={m.id} className="flex items-center gap-2">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-xs font-semibold text-primary">
                    {m.avatar_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={m.avatar_url} alt="" className="h-full w-full object-cover" />
                    ) : (
                      initials(m)
                    )}
                  </span>
                  <span className="min-w-0 flex-1 truncate text-sm">
                    {m.full_name ?? m.username ?? "User"}
                  </span>
                  {m.role === "owner" ? (
                    <Badge variant="secondary" className="gap-1">
                      <Crown className="h-3 w-3" /> Owner
                    </Badge>
                  ) : (
                    team.is_owner && (
                      <button
                        onClick={() => removeMember.mutate(m.id)}
                        className="text-muted-foreground hover:text-destructive"
                        aria-label="Remove member"
                        title="Remove member"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )
                  )}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Private prompts */}
        <div className="space-y-4 lg:col-span-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lock className="h-4 w-4" /> Private prompts — visible only to this team.
          </div>
          {prompts && prompts.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {prompts.map((p) => (
                <PromptCard key={p.id} prompt={p} />
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              No private prompts yet. When creating a prompt, choose this team under
              &ldquo;Visibility&rdquo; to keep it private here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
