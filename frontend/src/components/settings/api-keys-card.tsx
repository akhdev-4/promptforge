"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Copy, KeyRound, Loader2, Plus, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ApiError } from "@/lib/api";
import { apiKeysApi } from "@/lib/api-keys-api";
import { config } from "@/lib/config";
import { formatDate } from "@/lib/utils";
import type { ApiKeyCreated } from "@/types";

const KEYS_QUERY = ["api-keys"] as const;
const PUBLIC_BASE = `${config.apiBaseUrl}${config.apiV1}/public`;

function CopyButton({ value, label = "Copy" }: { value: string; label?: string }) {
  const [copied, setCopied] = React.useState(false);
  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      onClick={async () => {
        await navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
    >
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
      {copied ? "Copied" : label}
    </Button>
  );
}

export function ApiKeysCard() {
  const qc = useQueryClient();
  const { data: keys, isLoading } = useQuery({
    queryKey: KEYS_QUERY,
    queryFn: apiKeysApi.list,
  });

  const [name, setName] = React.useState("");
  const [write, setWrite] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  // The freshly-created key's secret — shown once, then dismissed.
  const [fresh, setFresh] = React.useState<ApiKeyCreated | null>(null);

  const create = useMutation({
    mutationFn: (vars: { name: string; write: boolean }) =>
      apiKeysApi.create(vars.name, vars.write),
    onSuccess: (created) => {
      setFresh(created);
      setName("");
      setWrite(false);
      void qc.invalidateQueries({ queryKey: KEYS_QUERY });
    },
    onError: (e) =>
      setError(e instanceof ApiError ? e.message : "Couldn't create the key."),
  });

  const revoke = useMutation({
    mutationFn: (id: string) => apiKeysApi.revoke(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: KEYS_QUERY }),
  });

  const onCreate = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (name.trim()) create.mutate({ name: name.trim(), write });
  };

  const active = keys?.filter((k) => !k.revoked_at) ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <KeyRound className="h-5 w-5" /> API keys
        </CardTitle>
        <CardDescription>
          Use PromptForge from the command line, the VS Code extension, or your own
          tools. Keys are read-only by default; grant write access to publish prompts.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Create */}
        <form onSubmit={onCreate} className="space-y-2.5">
          <div className="flex flex-wrap items-end gap-2">
            <div className="flex-1 space-y-1.5">
              <label className="text-xs text-muted-foreground">Key name</label>
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. My laptop CLI"
                maxLength={120}
              />
            </div>
            <Button type="submit" disabled={create.isPending || !name.trim()}>
              {create.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Create key
            </Button>
          </div>
          <label className="flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              checked={write}
              onChange={(e) => setWrite(e.target.checked)}
              className="mt-0.5"
            />
            <span>
              Allow publishing (write access)
              <span className="block text-xs text-muted-foreground">
                Lets this key create prompts (e.g. from the VS Code extension). Leave off
                for a safer read-only key.
              </span>
            </span>
          </label>
        </form>
        {error && <p className="text-xs text-destructive">{error}</p>}

        {/* One-time secret reveal */}
        {fresh && (
          <div className="space-y-2 rounded-xl border border-primary/40 bg-primary/5 p-4">
            <p className="text-sm font-medium">
              Copy your new key now — it won&rsquo;t be shown again.
            </p>
            <div className="flex items-center gap-2">
              <code className="flex-1 overflow-x-auto rounded-md bg-background px-3 py-2 font-mono text-xs">
                {fresh.key}
              </code>
              <CopyButton value={fresh.key} />
            </div>
            <button
              onClick={() => setFresh(null)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Done
            </button>
          </div>
        )}

        {/* Existing keys */}
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : active.length === 0 ? (
          <p className="text-sm text-muted-foreground">No active keys yet.</p>
        ) : (
          <div className="space-y-2">
            {active.map((k) => (
              <div
                key={k.id}
                className="flex items-center justify-between gap-3 rounded-lg border border-border px-3 py-2.5"
              >
                <div className="min-w-0">
                  <p className="flex items-center gap-2 truncate text-sm font-medium">
                    {k.name}
                    <span
                      className={`shrink-0 rounded-md px-1.5 py-0.5 text-[10px] font-medium ${
                        k.scopes?.includes("write")
                          ? "bg-amber-500/15 text-amber-600 dark:text-amber-400"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {k.scopes?.includes("write") ? "write" : "read-only"}
                    </span>
                  </p>
                  <p className="truncate font-mono text-xs text-muted-foreground">
                    {k.prefix}…{" · "}
                    {k.last_used_at
                      ? `last used ${formatDate(k.last_used_at)}`
                      : "never used"}
                  </p>
                </div>
                <button
                  onClick={() => revoke.mutate(k.id)}
                  disabled={revoke.isPending}
                  className="shrink-0 text-muted-foreground hover:text-destructive"
                  aria-label="Revoke key"
                  title="Revoke"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Usage hint */}
        <div className="space-y-1.5 rounded-lg bg-muted/50 p-3">
          <p className="text-xs font-medium text-muted-foreground">Try it</p>
          <div className="flex items-center gap-2">
            <code className="flex-1 overflow-x-auto rounded-md bg-background px-3 py-2 font-mono text-[11px]">
              curl -H &quot;X-API-Key: pf_…&quot; {PUBLIC_BASE}/prompts
            </code>
            <CopyButton
              value={`curl -H "X-API-Key: YOUR_KEY" ${PUBLIC_BASE}/prompts`}
              label="Copy"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
