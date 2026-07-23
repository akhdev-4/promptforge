"use client";

import { Check, Copy, FlaskConical, ImageIcon, Loader2, Play, Type } from "lucide-react";
import * as React from "react";

import { MarkdownView } from "@/components/prompts/markdown-view";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRunPrompt } from "@/hooks/use-playground";
import { type RunMode, streamRun } from "@/lib/playground-api";
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
  allowImage = true,
}: {
  promptId: string;
  content: string;
  defaultMode?: RunMode;
  allowImage?: boolean;
}) {
  const vars = React.useMemo(() => extractVars(content), [content]);
  const [values, setValues] = React.useState<Record<string, string>>({});
  const [mode, setMode] = React.useState<RunMode>(allowImage ? defaultMode : "text");
  const [copied, setCopied] = React.useState(false);

  // Text mode = streaming; image mode = one-shot mutation.
  const [streamText, setStreamText] = React.useState("");
  const [streaming, setStreaming] = React.useState(false);
  const [streamError, setStreamError] = React.useState<string | null>(null);
  const abortRef = React.useRef<AbortController | null>(null);

  const [imgLoading, setImgLoading] = React.useState(false);
  const image = useRunPrompt(promptId);

  React.useEffect(() => () => abortRef.current?.abort(), []);

  const changeMode = (next: RunMode) => {
    if (next === mode) return;
    abortRef.current?.abort();
    setMode(next);
    setStreamText("");
    setStreamError(null);
    setStreaming(false);
    setImgLoading(false);
    image.reset();
  };

  const runText = async () => {
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setStreamText("");
    setStreamError(null);
    setStreaming(true);
    try {
      await streamRun(promptId, values, (chunk) => setStreamText((t) => t + chunk), ctrl.signal);
    } catch (err) {
      if (!ctrl.signal.aborted) {
        setStreamError(err instanceof Error ? err.message : "Something went wrong.");
      }
    } finally {
      if (abortRef.current === ctrl) {
        setStreaming(false);
        abortRef.current = null;
      }
    }
  };

  const onRun = () => {
    if (mode === "image") {
      setImgLoading(true);
      image.mutate({ variables: values, mode: "image" });
    } else {
      void runText();
    }
  };

  const copy = async () => {
    if (!streamText) return;
    await navigator.clipboard.writeText(streamText);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const imgResult = image.data;
  const busy = streaming || image.isPending;

  return (
    <div className="space-y-4">
      <div>
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <FlaskConical className="h-4 w-4 text-primary" /> Run this prompt
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">See what this prompt produces.</p>
      </div>

      {allowImage && (
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
      )}

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

      <Button onClick={onRun} disabled={busy}>
        {busy ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : mode === "image" ? (
          <ImageIcon className="h-4 w-4" />
        ) : (
          <Play className="h-4 w-4" />
        )}
        {busy ? "Running…" : mode === "image" ? "Generate image" : "Run prompt"}
      </Button>

      {/* Image result */}
      {mode === "image" && image.isError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          Couldn&rsquo;t generate the image. Try again.
        </p>
      )}
      {mode === "image" && imgResult?.image_url && (
        <div className="space-y-2">
          <div className="relative flex min-h-[220px] items-center justify-center overflow-hidden rounded-xl border border-border bg-muted/40">
            {imgLoading && (
              <div className="absolute inset-0 flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Generating image…
              </div>
            )}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imgResult.image_url}
              alt="Generated result"
              className={cn("max-h-[440px] w-auto", imgLoading && "opacity-0")}
              onLoad={() => setImgLoading(false)}
              onError={() => setImgLoading(false)}
            />
          </div>
          <div className="flex items-center justify-between">
            <Badge variant="secondary">pollinations · free</Badge>
            <a
              href={imgResult.image_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
            >
              Open full size
            </a>
          </div>
        </div>
      )}

      {/* Text (streamed) result */}
      {mode === "text" && streamError && (
        <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {streamError}
        </p>
      )}
      {mode === "text" && (streaming || streamText) && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted-foreground">Output</span>
              {streaming && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Loader2 className="h-3 w-3 animate-spin" /> streaming…
                </span>
              )}
            </div>
            <Button variant="ghost" size="sm" onClick={copy} disabled={!streamText}>
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
          <div className="max-h-[480px] overflow-auto rounded-xl border border-border bg-muted/40 p-4 text-sm">
            <MarkdownView content={streamText || "…"} />
          </div>
        </div>
      )}
    </div>
  );
}
