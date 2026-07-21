"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Loader2 } from "lucide-react";
import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { authApi } from "@/lib/auth-api";
import { useAuthStore } from "@/stores/auth";

const schema = z.object({
  full_name: z.string().max(120).optional().or(z.literal("")),
  username: z
    .string()
    .min(3, "At least 3 characters")
    .max(50)
    .regex(/^[a-zA-Z0-9_-]+$/, "Letters, numbers, - and _ only")
    .optional()
    .or(z.literal("")),
  bio: z.string().max(500).optional().or(z.literal("")),
  avatar_url: z.url("Must be a URL").optional().or(z.literal("")),
});
type FormValues = z.infer<typeof schema>;

export function ProfileForm() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const [serverError, setServerError] = React.useState<string | null>(null);
  const [saved, setSaved] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    values: {
      full_name: user?.full_name ?? "",
      username: user?.username ?? "",
      bio: user?.bio ?? "",
      avatar_url: user?.avatar_url ?? "",
    },
  });

  const onSubmit = handleSubmit(async (values) => {
    setServerError(null);
    setSaved(false);
    try {
      const updated = await authApi.updateMe({
        full_name: values.full_name || null,
        username: values.username || null,
        bio: values.bio || null,
        avatar_url: values.avatar_url || null,
      });
      setUser(updated);
      reset(values); // clears dirty state
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Failed to save your profile.");
    }
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="full_name">Full name</Label>
        <Input id="full_name" autoComplete="name" {...register("full_name")} />
        {errors.full_name && <p className="text-xs text-destructive">{errors.full_name.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="username">Username</Label>
        <Input id="username" autoComplete="username" {...register("username")} />
        {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
        <p className="text-xs text-muted-foreground">Shown on your public profile and prompts.</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="bio">Bio</Label>
        <Textarea id="bio" placeholder="A short line about you." {...register("bio")} />
        {errors.bio && <p className="text-xs text-destructive">{errors.bio.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="avatar_url">Avatar URL</Label>
        <Input id="avatar_url" placeholder="https://…/avatar.png" {...register("avatar_url")} />
        {errors.avatar_url && (
          <p className="text-xs text-destructive">{errors.avatar_url.message}</p>
        )}
      </div>

      {serverError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {serverError}
        </p>
      )}

      <div className="flex items-center gap-3">
        <Button type="submit" disabled={isSubmitting || !isDirty}>
          {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
          Save changes
        </Button>
        {saved && (
          <span className="flex items-center gap-1 text-sm text-success">
            <Check className="h-4 w-4" /> Saved
          </span>
        )}
      </div>
    </form>
  );
}
