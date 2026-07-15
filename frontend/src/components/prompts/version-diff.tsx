"use client";

import { cn } from "@/lib/utils";
import type { VersionCompare } from "@/types";

const rowStyles: Record<string, string> = {
  equal: "text-muted-foreground",
  insert: "bg-success/10 text-foreground",
  delete: "bg-destructive/10 text-foreground",
};

const marker: Record<string, string> = { equal: " ", insert: "+", delete: "-" };

export function VersionDiff({ data }: { data: VersionCompare }) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="font-medium">
          v{data.from_version.version_number} → v{data.to_version.version_number}
        </span>
        <span className="text-success">+{data.added}</span>
        <span className="text-destructive">−{data.removed}</span>
      </div>

      <div className="overflow-x-auto rounded-xl border border-border bg-muted/30">
        <pre className="min-w-full font-mono text-xs leading-relaxed">
          {data.diff.map((line, i) => (
            <div
              key={i}
              className={cn("flex gap-3 px-3 py-0.5", rowStyles[line.op])}
            >
              <span className="select-none opacity-50">{marker[line.op]}</span>
              <span className="whitespace-pre-wrap break-words">{line.text || " "}</span>
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}
