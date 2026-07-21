"use client";

import { LogOut, Monitor, Moon, Sun, UserCog } from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const THEMES = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const;

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
            value={user.is_verified ? "Yes" : "No"}
          />
          <AccountRow label="Member since" value={formatDate(user.created_at)} />
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
