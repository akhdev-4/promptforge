"use client";

import { Compass, Loader2, LogOut, MailCheck, Monitor, Moon, Sun, UserCog } from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import { ApiKeysCard } from "@/components/settings/api-keys-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const THEMES = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const;

/** Inline "not verified yet" state with a one-click resend. */
function ResendVerification() {
  const [state, setState] = React.useState<"idle" | "sending" | "sent" | "error">("idle");
  const [note, setNote] = React.useState<string | null>(null);

  const send = async () => {
    setState("sending");
    try {
      const res = await authApi.resendVerification();
      setNote(
        res.email_sent
          ? "Confirmation link sent — check your inbox."
          : "Email isn't configured on this server, so nothing was sent.",
      );
      setState("sent");
    } catch (e) {
      setNote(e instanceof ApiError ? e.message : "Couldn't send the link.");
      setState("error");
    }
  };

  return (
    <span className="flex flex-col items-end gap-1">
      <span className="flex items-center gap-2">
        <span className="text-muted-foreground">No</span>
        <Button size="sm" variant="outline" onClick={send} disabled={state === "sending"}>
          {state === "sending" ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <MailCheck className="h-3.5 w-3.5" />
          )}
          Resend link
        </Button>
      </span>
      {note && (
        <span
          className={cn(
            "text-xs font-normal",
            state === "error" ? "text-destructive" : "text-muted-foreground",
          )}
        >
          {note}
        </span>
      )}
    </span>
  );
}

function AccountRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-2.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium">{value}</span>
    </div>
  );
}

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const router = useRouter();

  if (!user) return null;

  const onSignOut = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Appearance and account preferences.
        </p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Choose how PromptForge looks.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-3">
            {THEMES.map((t) => {
              const Icon = t.icon;
              const active = mounted && theme === t.value;
              return (
                <button
                  key={t.value}
                  onClick={() => setTheme(t.value)}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-xl border p-4 text-sm transition-colors",
                    active
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:bg-accent hover:text-foreground",
                  )}
                  aria-pressed={active}
                >
                  <Icon className="h-5 w-5" />
                  {t.label}
                </button>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Account */}
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Your account details.</CardDescription>
        </CardHeader>
        <CardContent className="divide-y divide-border pt-0">
          <AccountRow label="Name" value={user.full_name ?? "—"} />
          <AccountRow label="Username" value={user.username ? `@${user.username}` : "—"} />
          <AccountRow label="Email" value={user.email} />
          <AccountRow
            label="Role"
            value={
              <Badge variant="secondary" className="uppercase">
                {user.role}
              </Badge>
            }
          />
          <AccountRow
            label="Verified"
            value={user.is_verified ? "Yes" : <ResendVerification />}
          />
          <AccountRow label="Member since" value={formatDate(user.created_at)} />
        </CardContent>
      </Card>

      {/* Developer / API keys */}
      <ApiKeysCard />

      {/* Getting started */}
      <Card>
        <CardHeader>
          <CardTitle>Getting started</CardTitle>
          <CardDescription>New here, or want a refresher?</CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            variant="outline"
            onClick={() => window.dispatchEvent(new CustomEvent("pf:open-guide"))}
          >
            <Compass className="h-4 w-4" /> Replay the welcome guide
          </Button>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button variant="outline" asChild>
          <Link href="/profile">
            <UserCog className="h-4 w-4" /> Edit profile
          </Link>
        </Button>
        <Button variant="destructive" onClick={onSignOut}>
          <LogOut className="h-4 w-4" /> Sign out
        </Button>
      </div>
    </div>
  );
}
