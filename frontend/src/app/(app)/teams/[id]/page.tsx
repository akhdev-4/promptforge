"use client";

import {
  ArrowLeft,
  Check,
  Copy,
  Crown,
  Loader2,
  Lock,
  Mail,
  Trash2,
  UserPlus,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";

import { PromptCard } from "@/components/prompts/prompt-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useAddMember,
  useInviteMember,
  useRemoveMember,
  useRevokeInvite,
  useTeam,
  useTeamInvites,
  useTeamPrompts,
} from "@/hooks/use-teams";
import { ApiError } from "@/lib/api";
import type { InviteCreated } from "@/types";

function initials(m: { full_name: string | null; username: string | null }): string {
  const base = (m.full_name?.trim() || m.username?.trim() || "?").split(/\s+/);
  return (base[0]![0]! + (base[1]?.[0] ?? "")).toUpperCase();
}

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: team, isLoading, isError } = useTeam(id);
  const { data: prompts } = useTeamPrompts(id);
  const { data: invites } = useTeamInvites(id, Boolean(team?.is_owner));
  const addMember = useAddMember(id);
  const removeMember = useRemoveMember(id);
  const invite = useInviteMember(id);
  const revokeInvite = useRevokeInvite(id);
  const [username, setUsername] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [fresh, setFresh] = React.useState<InviteCreated | null>(null);
  const [copied, setCopied] = React.useState(false);

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

  const onInvite = async () => {
    if (!email.trim()) return;
    setError(null);
    try {
      const created = await invite.mutateAsync(email.trim());
      setFresh(created);
      setEmail("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't send that invite.");
    }
  };

  const copyLink = async (link: string) => {
    await navigator.clipboard.writeText(link);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
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
              <div className="space-y-2">
                {/* Invite by email */}
                <div className="flex gap-2">
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && onInvite()}
                    placeholder="Invite by email…"
                    className="h-9"
                  />
                  <Button
                    size="sm"
                    onClick={onInvite}
                    disabled={invite.isPending || !email.trim()}
                    title="Send invite"
                  >
                    {invite.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Mail className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {/* Freshly created invite — share the link */}
                {fresh && (
                  <div className="space-y-1 rounded-lg border border-primary/30 bg-primary/5 p-2 text-xs">
                    <p className="font-medium">
                      {fresh.email_sent
                        ? `Invite emailed to ${fresh.email}.`
                        : "Invite created — share this link:"}
                    </p>
                    <div className="flex items-center gap-1">
                      <code className="min-w-0 flex-1 truncate rounded bg-background px-2 py-1">
                        {fresh.link}
                      </code>
                      <button
                        onClick={() => copyLink(fresh.link)}
                        className="shrink-0 rounded p-1 text-muted-foreground hover:text-foreground"
                        aria-label="Copy link"
                      >
                        {copied ? (
                          <Check className="h-3.5 w-3.5" />
                        ) : (
                          <Copy className="h-3.5 w-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {/* Pending invites */}
                {invites && invites.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-[11px] font-medium text-muted-foreground">
                      Pending invites
                    </p>
                    {invites.map((inv) => (
                      <div key={inv.id} className="flex items-center gap-1 text-xs">
                        <Mail className="h-3 w-3 shrink-0 text-muted-foreground" />
                        <span className="min-w-0 flex-1 truncate">{inv.email}</span>
                        <button
                          onClick={() => revokeInvite.mutate(inv.id)}
                          className="shrink-0 text-muted-foreground hover:text-destructive"
                          aria-label="Revoke invite"
                          title="Revoke"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Quick add an existing member by username */}
                <div className="flex gap-2">
                  <Input
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && onAdd()}
                    placeholder="or add @username"
                    className="h-9"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={onAdd}
                    disabled={addMember.isPending || !username.trim()}
                    title="Add existing user"
                  >
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
