"use client";

import { Loader2, Plus, Trash2 } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useAddAsset, usePromptAssets, useRemoveAsset } from "@/hooks/use-prompts";
import { ApiError } from "@/lib/api";
import type { AssetKind } from "@/types";

const KIND_OPTIONS: [AssetKind, string][] = [
  ["screenshot", "Screenshot (URL)"],
  ["image", "Image (URL)"],
  ["video", "Video (URL)"],
  ["live_demo", "Live demo (URL)"],
  ["generated_html", "Generated HTML (inline)"],
  ["generated_code", "Generated code (inline)"],
];

const URL_KINDS: AssetKind[] = ["screenshot", "image", "video", "live_demo"];

export function AssetManager({ promptId }: { promptId: string }) {
  const { data: assets } = usePromptAssets(promptId);
  const add = useAddAsset(promptId);
  const remove = useRemoveAsset(promptId);

  const [kind, setKind] = React.useState<AssetKind>("screenshot");
  const [url, setUrl] = React.useState("");
  const [content, setContent] = React.useState("");
  const [language, setLanguage] = React.useState("");
  const [caption, setCaption] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const isUrl = URL_KINDS.includes(kind);

  const onAdd = async () => {
    setError(null);
    try {
      await add.mutateAsync({
        kind,
        url: isUrl ? url : null,
        content: isUrl ? null : content,
        language: kind === "generated_code" ? language || null : null,
        caption: caption || null,
      });
      setUrl("");
      setContent("");
      setCaption("");
      setLanguage("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to add asset.");
    }
  };

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-border p-4">
        <p className="mb-3 text-sm font-medium">Add a preview asset</p>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label>Type</Label>
            <Select value={kind} onChange={(e) => setKind(e.target.value as AssetKind)}>
              {KIND_OPTIONS.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-1.5">
            <Label>Caption (optional)</Label>
            <Input value={caption} onChange={(e) => setCaption(e.target.value)} />
          </div>
          {isUrl ? (
            <div className="space-y-1.5 sm:col-span-2">
              <Label>URL</Label>
              <Input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://…"
              />
            </div>
          ) : (
            <>
              {kind === "generated_code" && (
                <div className="space-y-1.5">
                  <Label>Language</Label>
                  <Input
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    placeholder="tsx"
                  />
                </div>
              )}
              <div className="space-y-1.5 sm:col-span-2">
                <Label>{kind === "generated_html" ? "HTML" : "Code"}</Label>
                <Textarea
                  className="min-h-32 font-mono text-xs"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder={kind === "generated_html" ? "<!doctype html>…" : "// code…"}
                />
              </div>
            </>
          )}
        </div>
        {error && <p className="mt-2 text-xs text-destructive">{error}</p>}
        <div className="mt-3 flex justify-end">
          <Button size="sm" onClick={onAdd} disabled={add.isPending}>
            {add.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Plus className="h-4 w-4" />
            )}
            Add asset
          </Button>
        </div>
      </div>

      {assets && assets.length > 0 && (
        <div className="space-y-2">
          {assets.map((a) => (
            <div
              key={a.id}
              className="flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm"
            >
              <div className="flex items-center gap-2 truncate">
                <span className="rounded-md bg-muted px-2 py-0.5 text-xs">{a.kind}</span>
                <span className="truncate text-muted-foreground">
                  {a.caption ?? a.url ?? a.language ?? "inline content"}
                </span>
              </div>
              <button
                onClick={() => remove.mutate(a.id)}
                className="text-muted-foreground hover:text-destructive"
                aria-label="Delete asset"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
