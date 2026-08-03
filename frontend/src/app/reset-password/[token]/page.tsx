"use client";

import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";
import { tokenStore } from "@/lib/token-store";
import { useAuthStore } from "@/stores/auth";

const MIN_LENGTH = 8;

export default function ResetPasswordPage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const setUser = useAuthStore((s) => s.setUser);

  const [password, setPassword] = React.useState("");
  const [confirm, setConfirm] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const reset = useMutation({
    mutationFn: () => authApi.resetPassword(token, password),
    onSuccess: async (tokens) => {
      // The reset endpoint signs us in, so store the tokens and load the user.
      tokenStore.set(tokens.access_token, tokens.refresh_token);
      setUser(await authApi.me());
      router.push("/dashboard");
    },
    onError: (e) =>
      setError(e instanceof ApiError ? e.message : "Couldn't reset your password."),
  });

  const tooShort = password.length > 0 && password.length < MIN_LENGTH;
  const mismatch = confirm.length > 0 && password !== confirm;
  const canSubmit = password.length >= MIN_LENGTH && password === confirm;

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 shadow-sm">
        <Logo className="mx-auto mb-4 h-12 w-auto" />
        <div className="text-center">
          <h1 className="text-lg font-semibold">Choose a new password</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            You&rsquo;ll be signed in once it&rsquo;s saved.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            setError(null);
            if (canSubmit) reset.mutate();
          }}
          className="mt-5 space-y-4"
        >
          <div className="space-y-1.5">
            <Label htmlFor="password">New password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required
            />
            {tooShort && (
              <p className="text-xs text-muted-foreground">
                At least {MIN_LENGTH} characters.
              </p>
            )}
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="confirm">Confirm password</Label>
            <Input
              id="confirm"
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
              required
            />
            {mismatch && (
              <p className="text-xs text-destructive">Passwords don&rsquo;t match.</p>
            )}
          </div>

          {error && <p className="text-xs text-destructive">{error}</p>}

          <Button type="submit" className="w-full" disabled={reset.isPending || !canSubmit}>
            {reset.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Save and sign in
          </Button>
          <Link
            href="/forgot-password"
            className="block text-center text-xs text-muted-foreground hover:text-foreground"
          >
            Need a new link?
          </Link>
        </form>
      </div>
    </div>
  );
}
