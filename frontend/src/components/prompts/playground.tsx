"use client";

import { Check, Copy, FlaskConical, ImageIcon, Loader2, Play, Type } from "lucide-react";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRunPrompt } from "@/hooks/use-playground";
import { ApiError } from "@/lib/api";
import type { RunMode } from "@/lib/playground-api";
import { cn } from "@/lib/utils";

const VAR_RE = /\{\{\s*([\w.\-]+)\s*\}\}/g;

function extractVars(content: string): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const m of content.matchAll(VAR_RE)) {
    if (!seen.has(m[1]!)) {
      seen.add(m[1]!);
      out.push(m[1]!);
    }
  }
  return out;
}

export function Playground({
  promptId,
  content,
  defaultMode = "text",
}: {
  promptId: string;
  content: string;
  defaultMode?: RunMode;
}) {
  const vars = React.useMemo(() => extractVars(content), [content]);
  const [values, setValues] = React.useState<Record<string, string>>({});
  const [mode, setMode] = React.useState<RunMode>(defaultMode);
  const [copied, setCopied] = React.useState(false);
  const [imgLoading, setImgLoading] = React.useState(false);
  const run = useRunPrompt(promptId);
  const result = run.data;

  const changeMode = (next: RunMode) => {
    if (next === mode) return;
    setMode(next);
    run.reset();
    setImgLoading(false);
  };

  const onRun = () => {
    if (mode === "image") setImgLoading(true);
    run.mutate({ variables: values, mode });
  };

  const copy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result.output);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <FlaskConical className="h-4 w-4 text-primary" /> Run this prompt
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">See what this prompt produces.</p>
      </div>

      {/* Text / Image mode toggle */}
      <div className="inline-flex rounded-lg border border-border p-0.5">
        {(
          [
            ["text", "Text", Type],
            ["image", "Image", ImageIcon],
          ] as const
        ).map(([value, label, Icon]) => (
          <button
            key={value}
            onClick={() => changeMode(value)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              mode === value
                ? "bg-primary text-primary-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            <Icon className="h-4 w-4" /> {label}
          </button>
        ))}
      </div>

      {mode === "image" && (
        <p className="text-xs text-muted-foreground">
          Generates a <strong>new</strong> image from the prompt text (free). It can&rsquo;t
          edit your own uploaded photo — that needs a paid image model.
        </p>
      )}

      {vars.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {vars.map((v) => (
            <div key={v} className="space-y-1">
              <Label htmlFor={`var-${v}`} className="text-xs">
                {v}
              </Label>
              <Input
                id={`var-${v}`}
                value={values[v] ?? ""}
                placeholder={`{{${v}}}`}
                onChange={(e) => setValues((s) => ({ ...s, [v]: e.target.value }))}
              />
            </div>
          ))}
        </div>
      )}

      <Button onClick={onRun} disabled={run.isPending}>
        {run.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : mode === "image" ? (
          <ImageIcon className="h-4 w-4" />
        ) : (
          <Play className="h-4 w-4" />
        )}
        {run.isPending ? "Running…" : mode === "image" ? "Generate image" : "Run prompt"}
      </Button>

      {run.isError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {run.error instanceof ApiError
            ? run.error.message
            : "Something went wrong running the prompt."}
        </p>
      )}

      {/* Image result */}
      {result?.image_url && (
        <div className="space-y-2">
          <div className="relative flex min-h-[220px] items-center justify-center overflow-hidden rounded-xl border border-border bg-muted/40">
            {imgLoading && (
              <div className="absolute inset-0 flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Generating image…
              </div>
            )}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={result.image_url}
              alt="Generated result"
              className={cn("max-h-[440px] w-auto", imgLoading && "opacity-0")}
              onLoad={() => setImgLoading(false)}
              onError={() => setImgLoading(false)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Badge variant="secondary">pollinations · free</Badge>
            <a
              href={result.image_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
            >
              Open full size
            </a>
          </div>
        </div>
      )}

      {/* Text result */}
      {result && !result.image_url && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Output</span>
              {result.is_demo ? (
                <Badge variant="warning">Demo</Badge>
              ) : (
                <Badge variant="secondary">{result.model ?? result.provider}</Badge>
              )}
            </div>
            <Button variant="ghost" size="sm" onClick={copy}>
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
          <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap rounded-xl border border-border bg-muted/40 p-4 text-sm">
            {result.output}
          </pre>
          {result.is_demo && (
            <p className="text-xs text-muted-foreground">
              This is placeholder output. Connect a Gemini key on the backend to see real
              results here — no code change needed.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
