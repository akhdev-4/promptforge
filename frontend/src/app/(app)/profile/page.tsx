"use client";

import { BadgeCheck, Mail } from "lucide-react";

import { ProfileForm } from "@/components/profile/profile-form";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

function initials(name: string | null, email: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    return (parts[0]![0] + (parts[1]?.[0] ?? "")).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  if (!user) return null;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage how you appear across PromptForge.
        </p>
      </div>

      {/* Identity header */}
      <Card>
        <CardContent className="flex flex-col items-center gap-4 p-6 text-center sm:flex-row sm:text-left">
          <span className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-2xl font-semibold text-primary">
            {user.avatar_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.avatar_url} alt="" className="h-full w-full object-cover" />
            ) : (
              initials(user.full_name, user.email)
            )}
          </span>
          <div className="space-y-1">
            <div className="flex items-center justify-center gap-2 sm:justify-start">
              <h2 className="text-lg font-semibold">
                {user.full_name ?? user.username ?? "Unnamed user"}
              </h2>
              {user.is_verified && <BadgeCheck className="h-4 w-4 text-primary" />}
            </div>
            {user.username && (
              <p className="text-sm text-muted-foreground">@{user.username}</p>
            )}
            <div className="flex flex-wrap items-center justify-center gap-2 pt-1 sm:justify-start">
              <Badge variant="secondary" className="uppercase">
                {user.role}
              </Badge>
              <span className="flex items-center gap-1 text-xs text-muted-foreground">
                <Mail className="h-3.5 w-3.5" /> {user.email}
              </span>
              <span className="text-xs text-muted-foreground">
                Joined {formatDate(user.created_at)}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Edit form */}
      <Card>
        <CardHeader>
          <CardTitle>Edit profile</CardTitle>
        </CardHeader>
        <CardContent>
          <ProfileForm />
        </CardContent>
      </Card>
    </div>
  );
}
