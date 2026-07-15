"use client";

import { MonitorPlay } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";
import type { PromptAsset } from "@/types";

/**
 * Renders interactive previews. Generated HTML is rendered from inline content
 * via a sandboxed iframe (`srcDoc`); live demos load an external URL. The
 * sandbox withholds same-origin access from inline HTML so untrusted preview
 * markup cannot touch the app.
 */
export function LivePreview({ assets }: { assets: PromptAsset[] }) {
  const previews = assets.filter(
    (a) =>
      (a.kind === "generated_html" && a.content) ||
      (a.kind === "live_demo" && a.url),
  );
  const [activeId, setActiveId] = React.useState(previews[0]?.id ?? "");
  const active = previews.find((p) => p.id === activeId) ?? previews[0];

  if (previews.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-14 text-center">
        <MonitorPlay className="h-9 w-9 text-muted-foreground/40" />
        <p className="mt-3 text-sm text-muted-foreground">No live preview available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {previews.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {previews.map((p, i) => (
            <button
              key={p.id}
              onClick={() => setActiveId(p.id)}
              className={cn(
                "rounded-lg border px-3 py-1.5 text-xs font-medium",
                p.id === (active?.id ?? "")
                  ? "border-primary/40 bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:text-foreground",
              )}
            >
              {p.caption ?? `${p.kind === "live_demo" ? "Live demo" : "Preview"} ${i + 1}`}
            </button>
          ))}
        </div>
      )}

      <div className="overflow-hidden rounded-xl border border-border bg-white">
        {active?.kind === "generated_html" ? (
          <iframe
            title={active.caption ?? "Generated preview"}
            srcDoc={active.content ?? ""}
            sandbox="allow-scripts"
            className="h-[32rem] w-full"
          />
        ) : (
          <iframe
            title={active?.caption ?? "Live demo"}
            src={active?.url ?? ""}
            sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
            className="h-[32rem] w-full"
          />
        )}
      </div>
    </div>
  );
}
