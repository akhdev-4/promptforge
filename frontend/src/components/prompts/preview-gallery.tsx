"use client";

import { ImageIcon, X } from "lucide-react";
import * as React from "react";

import type { PromptAsset } from "@/types";

export function PreviewGallery({ assets }: { assets: PromptAsset[] }) {
  const images = assets.filter(
    (a) => (a.kind === "screenshot" || a.kind === "image") && a.url,
  );
  const [active, setActive] = React.useState<PromptAsset | null>(null);

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-14 text-center">
        <ImageIcon className="h-9 w-9 text-muted-foreground/40" />
        <p className="mt-3 text-sm text-muted-foreground">No screenshots yet.</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {images.map((a) => (
          <button
            key={a.id}
            onClick={() => setActive(a)}
            className="group overflow-hidden rounded-xl border border-border bg-muted/30"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={a.url!}
              alt={a.caption ?? "Screenshot"}
              className="aspect-video w-full object-cover transition-transform group-hover:scale-[1.03]"
            />
            {a.caption && (
              <p className="truncate px-3 py-2 text-left text-xs text-muted-foreground">
                {a.caption}
              </p>
            )}
          </button>
        ))}
      </div>

      {active && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
          onClick={() => setActive(null)}
        >
          <button
            className="absolute right-4 top-4 rounded-full bg-white/10 p-2 text-white hover:bg-white/20"
            onClick={() => setActive(null)}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={active.url!}
            alt={active.caption ?? "Screenshot"}
            className="max-h-[90vh] max-w-full rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}
