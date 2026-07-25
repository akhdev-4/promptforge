"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, ExternalLink, Loader2, Package, Terminal, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ApiError } from "@/lib/api";
import { KIT_CATEGORIES, KIT_CATEGORY_LABEL } from "@/lib/kit-categories";
import { projectsApi } from "@/lib/projects-api";
import type { KitCategory, ProjectTemplate, TemplateUpsertInput } from "@/types";

function templateKey(id: string) {
  return ["project-template", id] as const;
}

export function TemplateSection({
  projectId,
  canManage,
}: {
  projectId: string;
  canManage: boolean;
}) {
  const qc = useQueryClient();
  const { data: template, isLoading } = useQuery({
    queryKey: templateKey(projectId),
    queryFn: async (): Promise<ProjectTemplate | null> => {
      try {
        return await projectsApi.getTemplate(projectId);
      } catch (e) {
        if (e instanceof ApiError && e.status === 404) return null;
        throw e;
      }
    },
  });

  const [editing, setEditing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const save = useMutation({
    mutationFn: (data: TemplateUpsertInput) => projectsApi.upsertTemplate(projectId, data),
    onSuccess: () => {
      setEditing(false);
      void qc.invalidateQueries({ queryKey: templateKey(projectId) });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Couldn't save."),
  });

  const remove = useMutation({
    mutationFn: () => projectsApi.deleteTemplate(projectId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: templateKey(projectId) }),
  });

  if (isLoading) return null;
  // Nothing to show to non-owners when the project isn't a template.
  if (!template && !canManage) return null;

  const showForm = editing || (!template && canManage);

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <Package className="h-4 w-4 text-primary" /> Starter template
        </CardTitle>
        {template && canManage && !editing && (
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => setEditing(true)}>
              Edit
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => remove.mutate()}
              disabled={remove.isPending}
              aria-label="Remove template"
            >
              <Trash2 className="h-4 w-4 text-muted-foreground" />
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {showForm ? (
          <TemplateForm
            initial={template ?? null}
            pending={save.isPending}
            error={error}
            onCancel={template ? () => setEditing(false) : undefined}
            onSubmit={(data) => {
              setError(null);
              save.mutate(data);
            }}
          />
        ) : template ? (
          <div className="space-y-2 text-sm">
            {template.category && (
              <span className="inline-block rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                {KIT_CATEGORY_LABEL[template.category]}
              </span>
            )}
            <a
              href={template.repo_url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 font-medium text-primary hover:underline"
            >
              <ExternalLink className="h-4 w-4" /> {template.repo_url}
            </a>
            {template.stack && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">Stack:</span> {template.stack}
              </p>
            )}
            {template.setup_command && (
              <code className="flex items-center gap-2 overflow-x-auto rounded-md bg-muted px-3 py-2 font-mono text-xs">
                <Terminal className="h-3.5 w-3.5 shrink-0" />
                {template.setup_command}
              </code>
            )}
            {template.notes && (
              <p className="whitespace-pre-wrap text-muted-foreground">{template.notes}</p>
            )}
            <Button size="sm" asChild>
              <a href={projectsApi.templateDownloadUrl(projectId)}>
                <Download className="h-4 w-4" /> Download codebase
              </a>
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}

function TemplateForm({
  initial,
  pending,
  error,
  onSubmit,
  onCancel,
}: {
  initial: ProjectTemplate | null;
  pending: boolean;
  error: string | null;
  onSubmit: (data: TemplateUpsertInput) => void;
  onCancel?: () => void;
}) {
  const [repoUrl, setRepoUrl] = React.useState(initial?.repo_url ?? "");
  const [category, setCategory] = React.useState<KitCategory | "">(initial?.category ?? "");
  const [stack, setStack] = React.useState(initial?.stack ?? "");
  const [setup, setSetup] = React.useState(initial?.setup_command ?? "");
  const [notes, setNotes] = React.useState(initial?.notes ?? "");

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        Point this project at a real codebase so others can pull it (soon, via the CLI).
      </p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label>Repository URL</Label>
          <Input
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/you/starter-store"
          />
        </div>
        <div className="space-y-1.5">
          <Label>Category</Label>
          <Select
            value={category}
            onChange={(e) => setCategory(e.target.value as KitCategory | "")}
          >
            <option value="">— none —</option>
            {KIT_CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </Select>
        </div>
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label>Stack (optional)</Label>
          <Input
            value={stack}
            onChange={(e) => setStack(e.target.value)}
            placeholder="Next.js + FastAPI + Stripe"
          />
        </div>
        <div className="space-y-1.5">
          <Label>Setup command (optional)</Label>
          <Input
            value={setup}
            onChange={(e) => setSetup(e.target.value)}
            placeholder="npm install && npm run dev"
          />
        </div>
      </div>
      <div className="space-y-1.5">
        <Label>Notes (optional)</Label>
        <Textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Anything a developer should know before running it…"
          className="min-h-20"
        />
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
      <div className="flex gap-2">
        <Button
          size="sm"
          disabled={pending || !repoUrl.trim()}
          onClick={() =>
            onSubmit({
              repo_url: repoUrl.trim(),
              category: category || null,
              stack: stack.trim() || null,
              setup_command: setup.trim() || null,
              notes: notes.trim() || null,
            })
          }
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
          Save template
        </Button>
        {onCancel && (
          <Button size="sm" variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </div>
  );
}
