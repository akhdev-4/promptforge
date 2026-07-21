"use client";

import { Camera, Check, Loader2, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

function initials(name: string | null, email: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    return (parts[0]![0] + (parts[1]?.[0] ?? "")).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

/** Avatar with a click-to-edit icon; sets the image via URL (no upload backend). */
export function AvatarEditor() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const [open, setOpen] = React.useState(false);
  const [url, setUrl] = React.useState("");
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;

  const openEditor = () => {
    setUrl(user.avatar_url ?? "");
    setError(null);
    setOpen(true);
  };

  const save = async (value: string | null) => {
    setSaving(true);
    setError(null);
    try {
      const updated = await authApi.updateMe({ avatar_url: value });
      setUser(updated);
      setOpen(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't update the photo.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <span className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-2xl font-semibold text-primary">
        {user.avatar_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={user.avatar_url} alt="" className="h-full w-full object-cover" />
        ) : (
          initials(user.full_name, user.email)
        )}
      </span>

      <button
        onClick={openEditor}
        className={cn(
          "absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full",
          "border-2 border-background bg-primary text-primary-foreground shadow-sm",
          "transition-transform hover:scale-105",
        )}
        aria-label="Change profile photo"
        title="Change profile photo"
      >
        <Camera className="h-3.5 w-3.5" />
      </button>

      {open && (
        <div className="absolute left-1/2 top-24 z-20 w-72 -translate-x-1/2 rounded-xl border border-border bg-popover p-3 shadow-lg">
          <p className="mb-2 text-xs font-medium text-muted-foreground">
            Paste an image URL for your photo
          </p>
          <Input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && save(url.trim() || null)}
            placeholder="https://…/photo.jpg"
            autoFocus
          />
          {error && <p className="mt-1.5 text-xs text-destructive">{error}</p>}
          <div className="mt-3 flex items-center justify-between gap-2">
            {user.avatar_url ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => save(null)}
                disabled={saving}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" /> Remove
              </Button>
            ) : (
              <span />
            )}
            <Button size="sm" onClick={() => save(url.trim() || null)} disabled={saving}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
              Save
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
