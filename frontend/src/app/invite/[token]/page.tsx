"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2, Users } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { teamsApi } from "@/lib/teams-api";
import { useAuthStore } from "@/stores/auth";

export default function InvitePage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const status = useAuthStore((s) => s.status);
  const [error, setError] = React.useState<string | null>(null);

  const { data: info, isLoading } = useQuery({
    queryKey: ["invite", token],
    queryFn: () => teamsApi.getInvite(token),
    retry: false,
  });

  const accept = useMutation({
    mutationFn: () => teamsApi.acceptInvite(token),
    onSuccess: (team) => router.push(`/teams/${team.id}`),
    onError: (e) =>
      setError(e instanceof ApiError ? e.message : "Couldn't accept the invitation."),
  });

  const card = (children: React.ReactNode) => (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center shadow-sm">
        <Logo className="mx-auto mb-4 h-12 w-auto" />
        {children}
      </div>
    </div>
  );

  if (isLoading || status === "loading" || status === "idle") {
    return card(<Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />);
  }

  if (!info) {
    return card(
      <>
        <h1 className="text-lg font-semibold">Invitation not found</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          This invite link is invalid or has been removed.
        </p>
        <Button asChild variant="outline" className="mt-4">
          <Link href="/">Go home</Link>
        </Button>
      </>,
    );
  }

  const invalid = info.expired || info.status !== "pending";

  return card(
    <>
      <span className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary/15 text-primary">
        <Users className="h-5 w-5" />
      </span>
      <h1 className="text-lg font-semibold">
        {invalid ? "This invitation is no longer valid" : `Join ${info.team_name}`}
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        {invalid
          ? info.expired
            ? "This invitation has expired. Ask the team owner for a new one."
            : "This invitation has already been used or revoked."
          : `You've been invited to the “${info.team_name}” team on PromptForge.`}
      </p>

      {!invalid && (
        <div className="mt-5 space-y-3">
          {!user ? (
            <>
              <p className="text-sm">
                Sign in (or sign up) with <strong>{info.email}</strong> to accept.
              </p>
              <div className="flex justify-center gap-2">
                <Button asChild>
                  <Link href="/login">Log in</Link>
                </Button>
                <Button asChild variant="outline">
                  <Link href="/register">Sign up</Link>
                </Button>
              </div>
            </>
          ) : user.email.toLowerCase() !== info.email.toLowerCase() ? (
            <p className="text-sm text-muted-foreground">
              This invite was sent to <strong>{info.email}</strong>, but you&rsquo;re signed
              in as {user.email}. Log out and sign in as the invited user to accept.
            </p>
          ) : (
            <>
              <Button
                className="w-full"
                onClick={() => accept.mutate()}
                disabled={accept.isPending}
              >
                {accept.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Accept &amp; join {info.team_name}
              </Button>
              {error && <p className="text-xs text-destructive">{error}</p>}
            </>
          )}
        </div>
      )}
    </>,
  );
}
