"use client";

import { Check, Copy, FlaskConical, Loader2, Play } from "lucide-react";
import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRunPrompt } from "@/hooks/use-playground";
import { ApiError } from "@/lib/api";

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

export function Playground({ promptId, content }: { promptId: string; content: string }) {
  const vars = React.useMemo(() => extractVars(content), [content]);
  const [values, setValues] = React.useState<Record<string, string>>({});
  const [copied, setCopied] = React.useState(false);
  const run = useRunPrompt(promptId);
  const result = run.data;

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
        <p className="mt-1 text-xs text-muted-foreground">
          See what this prompt actually produces.
          {vars.length > 0 && " Fill in the variables below, then run."}
        </p>
      </div>

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

      <Button onClick={() => run.mutate(values)} disabled={run.isPending}>
        {run.isPending ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Play className="h-4 w-4" />
        )}
        {run.isPending ? "Running…" : "Run prompt"}
      </Button>

      {run.isError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {run.error instanceof ApiError
            ? run.error.message
            : "Something went wrong running the prompt."}
        </p>
      )}

      {result && (
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
              This is placeholder output. Connect a free Gemini key on the backend to see
              real results here — no code change needed.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
