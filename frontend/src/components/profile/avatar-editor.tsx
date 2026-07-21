"use client";

import { Camera, Loader2, Trash2, Upload } from "lucide-react";
import * as React from "react";

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

/**
 * Resize a picked image to a small square-ish thumbnail and return a JPEG
 * data: URL — keeps the stored avatar tiny (~10–25KB) so it fits inline.
 */
function fileToThumbnail(file: File, max = 256, quality = 0.85): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Could not read the file"));
    reader.onload = () => {
      const img = new Image();
      img.onerror = () => reject(new Error("That file isn't a valid image"));
      img.onload = () => {
        const scale = Math.min(1, max / Math.max(img.width, img.height));
        const w = Math.max(1, Math.round(img.width * scale));
        const h = Math.max(1, Math.round(img.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        if (!ctx) return reject(new Error("Canvas not supported"));
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL("image/jpeg", quality));
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  });
}

export function AvatarEditor() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const [open, setOpen] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const ref = React.useRef<HTMLDivElement>(null);
  const fileRef = React.useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;

  const save = async (value: string | null) => {
    setBusy(true);
    setError(null);
    try {
      const updated = await authApi.updateMe({ avatar_url: value });
      setUser(updated);
      setOpen(false);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't update the photo.");
    } finally {
      setBusy(false);
    }
  };

  const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = ""; // allow re-picking the same file
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const thumb = await fileToThumbnail(file);
      await save(thumb);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't process the image.");
      setBusy(false);
    }
  };

  return (
    <div className="relative" ref={ref}>
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onFile}
      />

      <span className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-2xl font-semibold text-primary">
        {busy ? (
          <Loader2 className="h-6 w-6 animate-spin" />
        ) : user.avatar_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={user.avatar_url} alt="" className="h-full w-full object-cover" />
        ) : (
          initials(user.full_name, user.email)
        )}
      </span>

      <button
        onClick={() => setOpen((v) => !v)}
        disabled={busy}
        className={cn(
          "absolute -bottom-1 -right-1 flex h-7 w-7 items-center justify-center rounded-full",
          "border-2 border-background bg-primary text-primary-foreground shadow-sm",
          "transition-transform hover:scale-105 disabled:opacity-60",
        )}
        aria-label="Change profile photo"
        title="Change profile photo"
      >
        <Camera className="h-3.5 w-3.5" />
      </button>

      {open && !busy && (
        <div className="absolute left-1/2 top-24 z-20 w-56 -translate-x-1/2 rounded-xl border border-border bg-popover p-1.5 shadow-lg">
          <button
            onClick={() => fileRef.current?.click()}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-accent"
          >
            <Upload className="h-4 w-4" /> Upload a photo
          </button>
          {user.avatar_url && (
            <button
              onClick={() => save(null)}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="h-4 w-4" /> Remove photo
            </button>
          )}
          <p className="px-3 pb-1 pt-1.5 text-[11px] text-muted-foreground">
            JPG or PNG from your device.
          </p>
        </div>
      )}

      {error && (
        <p className="absolute left-1/2 top-24 z-20 w-56 -translate-x-1/2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
