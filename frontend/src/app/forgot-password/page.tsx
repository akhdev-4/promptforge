"use client";

import { useMutation } from "@tanstack/react-query";
import { ArrowLeft, Loader2, MailCheck } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Logo } from "@/components/brand/logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const request = useMutation({
    mutationFn: () => authApi.forgotPassword(email.trim()),
    onError: (e) =>
      setError(e instanceof ApiError ? e.message : "Something went wrong. Try again."),
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 shadow-sm">
        <Logo className="mx-auto mb-4 h-12 w-auto" />

        {request.isSuccess ? (
          <div className="text-center">
            <MailCheck className="mx-auto h-10 w-10 text-primary" />
            <h1 className="mt-3 text-lg font-semibold">Check your inbox</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              {request.data.detail}
            </p>
            {!request.data.email_sent && (
              <p className="mt-2 text-xs text-muted-foreground">
                Email delivery isn&rsquo;t configured on this server, so no message was
                actually sent.
              </p>
            )}
            <Button asChild variant="outline" className="mt-5 w-full">
              <Link href="/login">Back to login</Link>
            </Button>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setError(null);
              if (email.trim()) request.mutate();
            }}
            className="space-y-4"
          >
            <div className="text-center">
              <h1 className="text-lg font-semibold">Forgot your password?</h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Enter your email and we&rsquo;ll send you a link to choose a new one.
              </p>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            {error && <p className="text-xs text-destructive">{error}</p>}
            <Button
              type="submit"
              className="w-full"
              disabled={request.isPending || !email.trim()}
            >
              {request.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Send reset link
            </Button>
            <Link
              href="/login"
              className="flex items-center justify-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-3 w-3" /> Back to login
            </Link>
          </form>
        )}
      </div>
    </div>
  );
}
