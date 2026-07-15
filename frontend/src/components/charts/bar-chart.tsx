"use client";

import * as React from "react";

import type { TypeCount } from "@/lib/analytics-api";
import { promptTypeLabels } from "@/lib/prompt-meta";
import type { PromptType } from "@/types";

/**
 * Horizontal magnitude bars (prompt count by type). Single hue (primary),
 * 4px rounded data-ends anchored to the baseline, direct value labels,
 * per-bar hover highlight.
 */
export function BarChart({ data }: { data: TypeCount[] }) {
  const [hover, setHover] = React.useState<string | null>(null);
  if (data.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No data yet.</p>;
  }
  const max = Math.max(1, ...data.map((d) => d.count));

  return (
    <div className="space-y-2">
      {data.map((d) => {
        const label = promptTypeLabels[d.prompt_type as PromptType] ?? d.prompt_type;
        const pct = (d.count / max) * 100;
        const active = hover === d.prompt_type;
        return (
          <div
            key={d.prompt_type}
            className="flex items-center gap-3"
            onMouseEnter={() => setHover(d.prompt_type)}
            onMouseLeave={() => setHover(null)}
          >
            <span className="w-28 shrink-0 truncate text-right text-xs text-muted-foreground">
              {label}
            </span>
            <div className="relative h-5 flex-1 rounded-md bg-muted/40">
              <div
                className="h-5 rounded-md bg-primary transition-all"
                style={{ width: `${pct}%`, opacity: active ? 1 : 0.85 }}
              />
              <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] font-medium text-foreground">
                {d.count}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
