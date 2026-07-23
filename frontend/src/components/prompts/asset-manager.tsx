"use client";

import { Loader2, Plus, Trash2, Upload } from "lucide-react";
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
  ["screenshot", "Screenshot (upload or URL)"],
  ["image", "Image (upload or URL)"],
  ["video", "Video (URL)"],
  ["live_demo", "Live demo (URL)"],
  ["generated_html", "Generated HTML (inline)"],
  ["generated_code", "Generated code (inline)"],
];

const URL_KINDS: AssetKind[] = ["screenshot", "image", "video", "live_demo"];
const IMAGE_KINDS: AssetKind[] = ["screenshot", "image"];

/** Resize a picked/pasted image and return a compact JPEG data: URL. */
function fileToDataUrl(file: File, max = 1280, quality = 0.82): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Could not read the file"));
    reader.onload = () => {
      const img = new Image();
      img.onerror = () => reject(new Error("That file isn't a valid image"));
      img.onload = () => {
        const scale = Math.min(1, max / Math.max(img.width, img.height));
        const w = Math.max(1, Math.round(img.width * scale));
        const h = Math.max(1, Math.round(img.height * scale));
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        if (!ctx) return reject(new Error("Canvas not supported"));
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL("image/jpeg", quality));
      };
      img.src = reader.result as string;
    };
    reader.readAsDataURL(file);
  });
}

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
  const [processing, setProcessing] = React.useState(false);
  const fileRef = React.useRef<HTMLInputElement>(null);

  const isUrl = URL_KINDS.includes(kind);
  const canUpload = IMAGE_KINDS.includes(kind);
  const isUploaded = url.startsWith("data:");

  const processFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file.");
      return;
    }
    setError(null);
    setProcessing(true);
    try {
      setUrl(await fileToDataUrl(file));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Couldn't process the image.");
    } finally {
      setProcessing(false);
    }
  };

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) void processFile(file);
  };

  const onPaste = (e: React.ClipboardEvent) => {
    if (!canUpload) return;
    const item = Array.from(e.clipboardData.items).find((i) => i.type.startsWith("image/"));
    const file = item?.getAsFile();
    if (file) {
      e.preventDefault();
      void processFile(file);
    }
  };

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
      <div className="rounded-xl border border-border p-4" onPaste={onPaste}>
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
            <div className="space-y-2 sm:col-span-2">
              {canUpload && (
                <div className="flex flex-wrap items-center gap-2">
                  <input
                    ref={fileRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={onFile}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => fileRef.current?.click()}
                    disabled={processing}
                  >
                    {processing ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Upload className="h-4 w-4" />
                    )}
                    Upload image
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    or paste a screenshot (Ctrl/⌘+V), or use a URL below
                  </span>
                </div>
              )}

              {isUploaded ? (
                <div className="flex items-center gap-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={url}
                    alt="preview"
                    className="h-16 w-auto rounded-md border border-border object-cover"
                  />
                  <span className="text-xs text-muted-foreground">Image ready to add.</span>
                  <button
                    onClick={() => setUrl("")}
                    className="text-xs text-destructive hover:underline"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <div className="space-y-1.5">
                  <Label>URL</Label>
                  <Input
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://…"
                  />
                </div>
              )}
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
          <Button
            size="sm"
            onClick={onAdd}
            disabled={add.isPending || processing || (isUrl && !url) || (!isUrl && !content)}
          >
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
                  {a.caption ??
                    (a.url?.startsWith("data:") ? "uploaded image" : a.url) ??
                    a.language ??
                    "inline content"}
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
