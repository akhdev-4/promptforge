"use client";

import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import * as React from "react";

import { PromptForm } from "@/components/prompts/prompt-form";
import { ApiError } from "@/lib/api";
import { useCreatePrompt } from "@/hooks/use-prompts";
import type { PromptCreateInput } from "@/types";

export default function NewPromptPage() {
  return (
    <React.Suspense fallback={null}>
      <NewPromptForm />
    </React.Suspense>
  );
}

function NewPromptForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const componentId = searchParams.get("component_id");
  const create = useCreatePrompt();
  const [error, setError] = React.useState<string | null>(null);

  const onSubmit = async (data: PromptCreateInput) => {
    setError(null);
    try {
      const prompt = await create.mutateAsync(data);
      router.push(`/prompts/${prompt.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create prompt.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link
          href="/prompts"
          className="mb-2 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to library
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight">New Prompt</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Capture a production-tested prompt. Version 1 is created automatically.
          {componentId && " This prompt will be added to the selected component."}
        </p>
      </div>

      <PromptForm
        mode="create"
        submitting={create.isPending}
        serverError={error}
        componentId={componentId}
        onSubmit={onSubmit}
      />
    </div>
  );
}
