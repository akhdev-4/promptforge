"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ImagePlus, Loader2, Play, Plus, Trash2, Upload, Video, X } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { ApiError } from "@/lib/api";
import { fileToDataUrl } from "@/lib/image";
import { detectMedia } from "@/lib/media";
import { projectsApi } from "@/lib/projects-api";

function previewsKey(id: string) {
  return ["template-previews", id] as const;
}

/**
 * Grid thumbnail. Video previews play inline — muted and looping, which is what
 * browsers require to allow autoplay — so the tile behaves like a live preview.
 */
function Thumb({ url, alt }: { url: string; alt: string }) {
  const media = detectMedia(url);
  const frame = "aspect-video w-full object-cover transition group-hover:opacity-90";

  if (media.kind === "image") {
    // eslint-disable-next-line @next/next/no-img-element
    return <img src={url} alt={alt} className={frame} />;
  }

  return (
    <span className="relative block">
      {media.kind === "video" ? (
        // eslint-disable-next-line jsx-a11y/media-has-caption
        <video
          src={url}
          className={frame}
          autoPlay
          muted
          loop
          playsInline
          preload="metadata"
          poster={media.poster}
        />
      ) : (
        <iframe
          src={media.autoplaySrc ?? media.src}
          title={alt}
          loading="lazy"
          allow="autoplay; encrypted-media; picture-in-picture"
          // Clicks fall through to the button underneath, which opens the lightbox.
          className={`${frame} pointer-events-none border-0`}
        />
      )}
      {/* Hover affordance: the tile is silent, the lightbox has sound + controls. */}
      <span className="absolute inset-0 flex items-center justify-center opacity-0 transition group-hover:opacity-100">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-black/60 text-white backdrop-blur">
          <Play className="h-4 w-4 fill-current" />
        </span>
      </span>
    </span>
  );
}

export function TemplatePreviews({
  projectId,
  canManage,
}: {
  projectId: string;
  canManage: boolean;
}) {
  const qc = useQueryClient();
  const toast = useToast();
  const { data: previews } = useQuery({
    queryKey: previewsKey(projectId),
    queryFn: () => projectsApi.listPreviews(projectId),
  });

  const [caption, setCaption] = React.useState("");
  const [dataUrl, setDataUrl] = React.useState<string | null>(null);
  const [videoUrl, setVideoUrl] = React.useState("");
  const [processing, setProcessing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [lightbox, setLightbox] = React.useState<string | null>(null);
  const fileRef = React.useRef<HTMLInputElement>(null);

  const add = useMutation({
    mutationFn: (url: string) =>
      projectsApi.addPreview(projectId, { url, caption: caption.trim() || null }),
    onSuccess: () => {
      setDataUrl(null);
      setVideoUrl("");
      setCaption("");
      toast.success("Preview added.");
      void qc.invalidateQueries({ queryKey: previewsKey(projectId) });
    },
    onError: (e) => setError(e instanceof ApiError ? e.message : "Couldn't add the preview."),
  });

  const remove = useMutation({
    mutationFn: (id: string) => projectsApi.removePreview(projectId, id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: previewsKey(projectId) }),
  });

  const processFile = async (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please choose an image file.");
      return;
    }
    setError(null);
    setProcessing(true);
    try {
      setDataUrl(await fileToDataUrl(file));
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
    const item = Array.from(e.clipboardData.items).find((i) => i.type.startsWith("image/"));
    const file = item?.getAsFile();
    if (file) {
      e.preventDefault();
      void processFile(file);
    }
  };

  const items = previews ?? [];
  if (items.length === 0 && !canManage) return null;

  return (
    <div className="space-y-3 border-t border-border pt-4">
      <p className="flex items-center gap-2 text-sm font-medium">
        <ImagePlus className="h-4 w-4 text-primary" /> Preview
      </p>

      {items.length > 0 ? (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {items.map((p) => (
            <figure key={p.id} className="group relative">
              <button
                onClick={() => setLightbox(p.url)}
                className="block w-full overflow-hidden rounded-lg border border-border"
              >
                <Thumb url={p.url} alt={p.caption ?? "preview"} />
              </button>
              {p.caption && (
                <figcaption className="mt-1 truncate text-xs text-muted-foreground">
                  {p.caption}
                </figcaption>
              )}
              {canManage && (
                <button
                  onClick={() => remove.mutate(p.id)}
                  className="absolute right-1.5 top-1.5 rounded-md bg-background/80 p-1 text-muted-foreground opacity-0 backdrop-blur transition hover:text-destructive group-hover:opacity-100"
                  aria-label="Delete preview"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </figure>
          ))}
        </div>
      ) : (
        canManage && (
          <p className="text-sm text-muted-foreground">
            No previews yet. Add screenshots of the running app (login, products, cart,
            checkout…) or a walkthrough video link so people can see what it looks like.
          </p>
        )
      )}

      {/* Owner uploader */}
      {canManage && (
        <div className="rounded-lg border border-dashed border-border p-3" onPaste={onPaste}>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={onFile}
          />
          {dataUrl ? (
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={dataUrl}
                  alt="new preview"
                  className="h-16 w-auto rounded-md border border-border object-cover"
                />
                <button
                  onClick={() => setDataUrl(null)}
                  className="text-xs text-destructive hover:underline"
                >
                  Remove
                </button>
              </div>
              <Input
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                placeholder="Caption (e.g. Checkout screen)"
                maxLength={120}
              />
              <Button
                size="sm"
                onClick={() => add.mutate(dataUrl)}
                disabled={add.isPending}
              >
                {add.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                Add preview
              </Button>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2">
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
                  Upload screenshot
                </Button>
                <span className="text-xs text-muted-foreground">
                  or paste an image (Ctrl/⌘+V)
                </span>
              </div>

              {/* Video previews live at a URL — files are far too large to inline. */}
              <div className="flex gap-2">
                <Input
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && videoUrl.trim()) add.mutate(videoUrl.trim());
                  }}
                  placeholder="…or paste a video link (YouTube, Loom, Vimeo, .mp4)"
                  className="h-9"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => add.mutate(videoUrl.trim())}
                  disabled={add.isPending || !videoUrl.trim()}
                  title="Add video preview"
                >
                  {add.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Video className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          )}
          {error && <p className="mt-2 text-xs text-destructive">{error}</p>}
        </div>
      )}

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-[95] flex items-center justify-center bg-black/80 p-6"
          onClick={() => setLightbox(null)}
        >
          <button
            className="absolute right-4 top-4 rounded-md bg-background/70 p-1.5 text-foreground"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
          {/* Stop propagation so clicking the player doesn't close the lightbox. */}
          <div onClick={(e) => e.stopPropagation()} className="max-h-full w-full max-w-4xl">
            {(() => {
              const media = detectMedia(lightbox);
              if (media.kind === "embed") {
                return (
                  <iframe
                    src={media.src}
                    title="preview"
                    className="aspect-video w-full rounded-lg"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; picture-in-picture; fullscreen"
                    allowFullScreen
                  />
                );
              }
              if (media.kind === "video") {
                return (
                  // eslint-disable-next-line jsx-a11y/media-has-caption
                  <video
                    src={media.src}
                    controls
                    autoPlay
                    playsInline
                    className="max-h-[85vh] w-full rounded-lg"
                  />
                );
              }
              return (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={lightbox}
                  alt="preview"
                  className="mx-auto max-h-[85vh] max-w-full rounded-lg object-contain"
                />
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}
