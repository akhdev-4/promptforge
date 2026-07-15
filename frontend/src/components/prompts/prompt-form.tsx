"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { TagInput } from "@/components/prompts/tag-input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useCategoryTree, usePopularTags } from "@/hooks/use-taxonomy";
import {
  complexityOptions,
  promptTypeOptions,
  statusOptions,
} from "@/lib/prompt-meta";
import type { CategoryNode, PromptCreateInput, PromptDetail } from "@/types";

/** Flatten a category tree into indented <option> rows. */
function flattenCategories(
  nodes: CategoryNode[],
  depth = 0,
): { id: string; label: string }[] {
  return nodes.flatMap((n) => [
    { id: n.id, label: `${"— ".repeat(depth)}${n.name}` },
    ...flattenCategories(n.children ?? [], depth + 1),
  ]);
}

const schema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().max(1000).optional(),
  content: z.string().optional(), // required only in create mode (checked below)
  prompt_type: z.string(),
  complexity: z.string(),
  status: z.string(),
  framework: z.string().max(60).optional(),
  language: z.string().max(60).optional(),
  ai_model: z.string().max(60).optional(),
  category_id: z.string().optional(),
  estimated_tokens: z.string().optional(),
  expected_output: z.string().optional(),
  demo_url: z.url("Must be a URL").optional().or(z.literal("")),
  repository_url: z.url("Must be a URL").optional().or(z.literal("")),
});

type FormValues = z.infer<typeof schema>;

interface PromptFormProps {
  mode: "create" | "edit";
  initial?: PromptDetail;
  submitting?: boolean;
  serverError?: string | null;
  /** Pre-assign the prompt to a component (e.g. when adding a variant). */
  componentId?: string | null;
  onSubmit: (data: PromptCreateInput) => void;
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}

export function PromptForm({
  mode,
  initial,
  submitting,
  serverError,
  onSubmit,
  componentId,
}: PromptFormProps) {
  const { data: tree } = useCategoryTree();
  const { data: popularTags } = usePopularTags();
  const categoryOptions = React.useMemo(() => flattenCategories(tree ?? []), [tree]);
  const [tags, setTags] = React.useState<string[]>(
    initial?.tags.map((t) => t.name) ?? [],
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: initial?.title ?? "",
      description: initial?.description ?? "",
      content: initial?.content ?? "",
      prompt_type: initial?.prompt_type ?? "ui",
      complexity: initial?.complexity ?? "intermediate",
      status: initial?.status ?? "published",
      framework: initial?.framework ?? "",
      language: initial?.language ?? "",
      ai_model: initial?.ai_model ?? "",
      category_id: initial?.category?.id ?? "",
      estimated_tokens:
        initial?.estimated_tokens != null ? String(initial.estimated_tokens) : "",
      expected_output: initial?.expected_output ?? "",
      demo_url: initial?.demo_url ?? "",
      repository_url: initial?.repository_url ?? "",
    },
  });

  const submit = handleSubmit((values) => {
    if (mode === "create" && (!values.content || values.content.trim() === "")) {
      // Surface as a field-level error without a resolver refinement.
      window.alert("Prompt content is required.");
      return;
    }
    const tokensRaw = values.estimated_tokens?.trim();
    const tokensNum = tokensRaw ? Number(tokensRaw) : NaN;
    onSubmit({
      title: values.title,
      content: values.content ?? "",
      description: values.description || null,
      prompt_type: values.prompt_type as PromptCreateInput["prompt_type"],
      complexity: values.complexity as PromptCreateInput["complexity"],
      status: values.status as PromptCreateInput["status"],
      framework: values.framework || null,
      language: values.language || null,
      ai_model: values.ai_model || null,
      category_id: values.category_id || null,
      component_id: componentId ?? initial?.component?.id ?? null,
      tags,
      estimated_tokens: Number.isFinite(tokensNum) ? tokensNum : null,
      expected_output: values.expected_output || null,
      demo_url: values.demo_url || null,
      repository_url: values.repository_url || null,
    });
  });

  return (
    <form onSubmit={submit} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Field label="Title" error={errors.title?.message}>
            <Input placeholder="Modern Glassmorphism Login" {...register("title")} />
          </Field>
          <Field label="Description" error={errors.description?.message}>
            <Textarea
              placeholder="A short summary of what this prompt produces."
              {...register("description")}
            />
          </Field>

          {mode === "create" && (
            <Field label="Prompt content" error={errors.content?.message}>
              <Textarea
                className="min-h-64 font-mono text-xs"
                placeholder="Paste your production-tested prompt here…"
                {...register("content")}
              />
            </Field>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Classification</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Field label="Type">
            <Select {...register("prompt_type")}>
              {promptTypeOptions.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Complexity">
            <Select {...register("complexity")}>
              {complexityOptions.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Status">
            <Select {...register("status")}>
              {statusOptions.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </Select>
          </Field>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Category &amp; tags</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Field label="Category">
            <Select {...register("category_id")}>
              <option value="">Uncategorized</option>
              {categoryOptions.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.label}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Tags">
            <TagInput
              value={tags}
              onChange={setTags}
              suggestions={(popularTags ?? []).map((t) => t.name)}
              placeholder="Add tags (Enter or comma)…"
            />
          </Field>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tech &amp; references</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Field label="Framework">
            <Input placeholder="React" {...register("framework")} />
          </Field>
          <Field label="Language">
            <Input placeholder="TypeScript" {...register("language")} />
          </Field>
          <Field label="AI model">
            <Input placeholder="claude-opus-4-8" {...register("ai_model")} />
          </Field>
          <Field label="Estimated tokens" error={errors.estimated_tokens?.message}>
            <Input type="number" min={0} {...register("estimated_tokens")} />
          </Field>
          <Field label="Demo URL" error={errors.demo_url?.message}>
            <Input placeholder="https://…" {...register("demo_url")} />
          </Field>
          <Field label="Repository URL" error={errors.repository_url?.message}>
            <Input placeholder="https://github.com/…" {...register("repository_url")} />
          </Field>
          <div className="sm:col-span-3">
            <Field label="Expected output">
              <Textarea
                placeholder="What good output from this prompt looks like."
                {...register("expected_output")}
              />
            </Field>
          </div>
        </CardContent>
      </Card>

      {serverError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {serverError}
        </p>
      )}

      <div className="flex justify-end gap-3">
        <Button type="submit" disabled={submitting}>
          {submitting && <Loader2 className="h-4 w-4 animate-spin" />}
          {mode === "create" ? "Create prompt" : "Save changes"}
        </Button>
      </div>
    </form>
  );
}
