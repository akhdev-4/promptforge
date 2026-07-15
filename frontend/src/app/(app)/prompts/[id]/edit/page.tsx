"use client";

import { ArrowLeft, GitCommitHorizontal, Loader2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { PromptForm } from "@/components/prompts/prompt-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { useAddVersion, usePrompt, useUpdatePrompt } from "@/hooks/use-prompts";
import { useAuthStore } from "@/stores/auth";
import type { PromptCreateInput } from "@/types";

export default function EditPromptPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const { data: prompt, isLoading } = usePrompt(id);
  const update = useUpdatePrompt(id);
  const addVersion = useAddVersion(id);

  const [metaError, setMetaError] = React.useState<string | null>(null);
  const [versionContent, setVersionContent] = React.useState("");
  const [summary, setSummary] = React.useState("");
  const [versionError, setVersionError] = React.useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Skeleton className="h-8 w-1/2" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }
  if (!prompt) {
    return <div className="text-sm text-destructive">Prompt not found.</div>;
  }

  const isOwner = user?.id === prompt.author.id;
  const canModerate = user?.role === "moderator" || user?.role === "administrator";
  if (!isOwner && !canModerate) {
    return (
      <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
        You do not have permission to edit this prompt.
      </div>
    );
  }

  const onSaveMeta = async (data: PromptCreateInput) => {
    setMetaError(null);
    try {
      // Metadata only — content is versioned separately below.
      const { content: _content, ...meta } = data;
      void _content;
      await update.mutateAsync(meta);
      router.push(`/prompts/${prompt.id}`);
    } catch (err) {
      setMetaError(err instanceof ApiError ? err.message : "Failed to save changes.");
    }
  };

  const onAddVersion = async () => {
    setVersionError(null);
    if (!versionContent.trim()) {
      setVersionError("Version content is required.");
      return;
    }
    try {
      await addVersion.mutateAsync({
        content: versionContent,
        change_summary: summary || undefined,
      });
      router.push(`/prompts/${prompt.id}`);
    } catch (err) {
      setVersionError(err instanceof ApiError ? err.message : "Failed to add version.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <Link
          href={`/prompts/${prompt.id}`}
          className="mb-2 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to prompt
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight">Edit “{prompt.title}”</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Metadata changes save in place. New prompt content creates a new version.
        </p>
      </div>

      {/* Add version panel */}
      <Card className="border-primary/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitCommitHorizontal className="h-4 w-4 text-primary" />
            New version (currently v{prompt.current_version})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>New prompt content</Label>
            <Textarea
              className="min-h-48 font-mono text-xs"
              value={versionContent}
              onChange={(e) => setVersionContent(e.target.value)}
              placeholder="Paste the improved prompt content for the next version…"
            />
          </div>
          <div className="space-y-2">
            <Label>Change summary</Label>
            <Input
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              placeholder="e.g. Add dark mode + accessibility"
            />
          </div>
          {versionError && <p className="text-xs text-destructive">{versionError}</p>}
          <div className="flex justify-end">
            <Button onClick={onAddVersion} disabled={addVersion.isPending}>
              {addVersion.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Commit v{prompt.current_version + 1}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Metadata form */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Metadata</h2>
        <PromptForm
          mode="edit"
          initial={prompt}
          submitting={update.isPending}
          serverError={metaError}
          onSubmit={onSaveMeta}
        />
      </div>
    </div>
  );
}
