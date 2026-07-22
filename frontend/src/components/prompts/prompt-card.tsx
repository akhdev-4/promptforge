import { Copy, Eye, GitFork, Layers, Play } from "lucide-react";
import Link from "next/link";

import { StarRating } from "@/components/prompts/star-rating";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { complexityLabels, promptTypeLabels } from "@/lib/prompt-meta";
import type { PromptSummary } from "@/types";

function Stat({ icon: Icon, value }: { icon: typeof Eye; value: number }) {
  return (
    <span className="flex items-center gap-1 text-xs text-muted-foreground">
      <Icon className="h-3.5 w-3.5" />
      {value}
    </span>
  );
}

export function PromptCard({ prompt }: { prompt: PromptSummary }) {
  return (
    <Card className="group relative flex h-full flex-col p-5 transition-all hover:border-primary/40 hover:shadow-md">
      {/* Whole-card click target → prompt detail. Sits above the static content
          but below the interactive Run button (which is relatively positioned). */}
      <Link
        href={`/prompts/${prompt.id}`}
        className="absolute inset-0"
        aria-label={prompt.title}
      />

      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <Badge variant="default">{promptTypeLabels[prompt.prompt_type]}</Badge>
          {prompt.category && (
            <span className="text-xs text-muted-foreground">{prompt.category.name}</span>
          )}
        </div>
        {prompt.status === "draft" && <Badge variant="warning">Draft</Badge>}
      </div>

      <h3 className="line-clamp-1 font-semibold tracking-tight group-hover:text-primary">
        {prompt.title}
      </h3>
      <p className="mt-1 line-clamp-2 flex-1 text-sm text-muted-foreground">
        {prompt.description ?? "No description provided."}
      </p>

      <div className="mt-3 flex items-center gap-1.5">
        <StarRating value={prompt.rating_avg} readOnly size="sm" />
        <span className="text-xs text-muted-foreground">
          {prompt.rating_count > 0
            ? `${prompt.rating_avg.toFixed(1)} (${prompt.rating_count})`
            : "Not rated yet"}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {prompt.framework && <Badge variant="outline">{prompt.framework}</Badge>}
        {prompt.language && <Badge variant="outline">{prompt.language}</Badge>}
        <Badge variant="secondary">{complexityLabels[prompt.complexity]}</Badge>
        {prompt.tags.slice(0, 3).map((t) => (
          <span key={t.id} className="text-xs text-primary/80">
            #{t.slug}
          </span>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
        <div className="flex items-center gap-3">
          <Stat icon={Eye} value={prompt.views_count} />
          <Stat icon={Copy} value={prompt.copies_count} />
          <Stat icon={GitFork} value={prompt.forks_count} />
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Layers className="h-3.5 w-3.5" />v{prompt.current_version}
          </span>
        </div>
        <Link
          href={`/prompts/${prompt.id}?tab=playground`}
          className="relative z-10 inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/10"
          title="Run this prompt in the Playground"
        >
          <Play className="h-3.5 w-3.5" /> Run
        </Link>
      </div>
    </Card>
  );
}
