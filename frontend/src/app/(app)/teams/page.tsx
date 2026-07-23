"use client";

import { Crown, Loader2, Plus, Users } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCreateTeam, useTeams } from "@/hooks/use-teams";

export default function TeamsPage() {
  const { data: teams, isLoading } = useTeams();
  const create = useCreateTeam();
  const [name, setName] = React.useState("");

  const onCreate = async () => {
    if (!name.trim()) return;
    await create.mutateAsync({ name: name.trim() });
    setName("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Teams</h1>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Shared workspaces. Prompts you assign to a team are <strong>private</strong> — only
          members can see them.
        </p>
      </div>

      <div className="flex gap-2">
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && onCreate()}
          placeholder="New team name (e.g. Design Guild)"
          className="max-w-sm"
        />
        <Button onClick={onCreate} disabled={create.isPending || !name.trim()}>
          {create.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Plus className="h-4 w-4" />
          )}
          Create team
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))}
        </div>
      ) : teams && teams.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {teams.map((t) => (
            <Link key={t.id} href={`/teams/${t.id}`}>
              <Card className="h-full p-5 transition-all hover:border-primary/40 hover:shadow-md">
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                    <Users className="h-5 w-5" />
                  </div>
                  {t.is_owner && (
                    <Badge variant="secondary" className="gap-1">
                      <Crown className="h-3 w-3" /> Owner
                    </Badge>
                  )}
                </div>
                <h3 className="mt-3 font-semibold">{t.name}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">
                  {t.description ?? "No description."}
                </p>
                <p className="mt-3 text-xs text-muted-foreground">
                  {t.member_count} member{t.member_count === 1 ? "" : "s"}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Users className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No teams yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Create a team to share private prompts with a group.
          </p>
        </div>
      )}
    </div>
  );
}
