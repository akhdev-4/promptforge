"use client";

import { Code2 } from "lucide-react";
import * as React from "react";

import { CopyButton } from "@/components/prompts/copy-button";
import { MarkdownView } from "@/components/prompts/markdown-view";
import { cn } from "@/lib/utils";
import type { PromptAsset } from "@/types";

export function CodeView({
  assets,
  promptId,
}: {
  assets: PromptAsset[];
  promptId: string;
}) {
  const codes = assets.filter((a) => a.kind === "generated_code" && a.content);
  const [activeId, setActiveId] = React.useState(codes[0]?.id ?? "");
  const active = codes.find((c) => c.id === activeId) ?? codes[0];

  if (codes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-14 text-center">
        <Code2 className="h-9 w-9 text-muted-foreground/40" />
        <p className="mt-3 text-sm text-muted-foreground">No generated code attached.</p>
      </div>
    );
  }

  const fenced = "```" + (active?.language ?? "") + "\n" + (active?.content ?? "") + "\n```";

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          {codes.map((c, i) => (
            <button
              key={c.id}
              onClick={() => setActiveId(c.id)}
              className={cn(
                "rounded-lg border px-3 py-1.5 text-xs font-medium",
                c.id === (active?.id ?? "")
                  ? "border-primary/40 bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:text-foreground",
              )}
            >
              {c.caption ?? c.language ?? `Snippet ${i + 1}`}
            </button>
          ))}
        </div>
        {active?.content && (
          <CopyButton
            promptId={promptId}
            content={active.content}
            variant="ghost"
            size="sm"
            label="Copy code"
          />
        )}
      </div>
      <MarkdownView content={fenced} />
    </div>
  );
}
