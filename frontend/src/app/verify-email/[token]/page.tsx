"use client";

import { useMutation } from "@tanstack/react-query";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import * as React from "react";

import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";

export default function VerifyEmailPage() {
  const { token } = useParams<{ token: string }>();
  const [error, setError] = React.useState<string | null>(null);

  const verify = useMutation({
    mutationFn: () => authApi.verifyEmail(token),
    onError: (e) =>
      setError(e instanceof ApiError ? e.message : "Couldn't confirm this link."),
  });

  // Confirm as soon as the page opens — the click *is* the confirmation.
  const run = verify.mutate;
  React.useEffect(() => {
    run();
  }, [run]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center shadow-sm">
        <Logo className="mx-auto mb-4 h-12 w-auto" />

        {verify.isPending && (
          <>
            <Loader2 className="mx-auto h-6 w-6 animate-spin text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">Confirming your email…</p>
          </>
        )}

        {verify.isSuccess && (
          <>
            <CheckCircle2 className="mx-auto h-10 w-10 text-green-600" />
            <h1 className="mt-3 text-lg font-semibold">Email confirmed</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Your account is all set. Welcome to PromptForge.
            </p>
            <Button asChild className="mt-5 w-full">
              <Link href="/dashboard">Go to dashboard</Link>
            </Button>
          </>
        )}

        {verify.isError && (
          <>
            <XCircle className="mx-auto h-10 w-10 text-destructive" />
            <h1 className="mt-3 text-lg font-semibold">Link didn&rsquo;t work</h1>
            <p className="mt-1 text-sm text-muted-foreground">{error}</p>
            <p className="mt-2 text-xs text-muted-foreground">
              Confirmation links expire and can only be used once. Sign in and request a
              new one from your profile.
            </p>
            <Button asChild variant="outline" className="mt-5 w-full">
              <Link href="/login">Go to login</Link>
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
