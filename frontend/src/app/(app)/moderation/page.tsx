"use client";

import { ExternalLink, Shield } from "lucide-react";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useReports, useUpdateReport } from "@/hooks/use-community";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const STATUS_VARIANT: Record<string, "warning" | "success" | "secondary"> = {
  open: "warning",
  resolved: "success",
  dismissed: "secondary",
};

export default function ModerationPage() {
  const role = useAuthStore((s) => s.user?.role);
  const canModerate = role === "moderator" || role === "administrator";
  const { data: reports, isLoading } = useReports();
  const update = useUpdateReport();

  if (!canModerate) {
    return (
      <p className="text-sm text-muted-foreground">
        You don&rsquo;t have access to moderation.
      </p>
    );
  }

  const openCount = reports?.filter((r) => r.status === "open").length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Shield className="h-6 w-6 text-primary" /> Moderation
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Reported prompts. {openCount} open report{openCount === 1 ? "" : "s"}.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-20 w-full rounded-xl" />
          ))}
        </div>
      ) : reports && reports.length > 0 ? (
        <div className="space-y-3">
          {reports.map((r) => (
            <div
              key={r.id}
              className="flex flex-col gap-3 rounded-xl border border-border p-4 sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <Link
                    href={`/prompts/${r.prompt.id}`}
                    className="inline-flex items-center gap-1 font-medium hover:text-primary"
                  >
                    {r.prompt.title} <ExternalLink className="h-3.5 w-3.5" />
                  </Link>
                  <Badge variant={STATUS_VARIANT[r.status] ?? "secondary"} className="uppercase">
                    {r.status}
                  </Badge>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  &ldquo;{r.reason}&rdquo;
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  by {r.reporter?.username ?? "unknown"} · {formatDate(r.created_at)}
                </p>
              </div>
              {r.status === "open" && (
                <div className="flex shrink-0 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={update.isPending}
                    onClick={() => update.mutate({ id: r.id, status: "dismissed" })}
                  >
                    Dismiss
                  </Button>
                  <Button
                    size="sm"
                    disabled={update.isPending}
                    onClick={() => update.mutate({ id: r.id, status: "resolved" })}
                  >
                    Resolve
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16 text-center">
          <Shield className="h-10 w-10 text-muted-foreground/40" />
          <p className="mt-3 font-medium">No reports</p>
          <p className="mt-1 text-sm text-muted-foreground">The library is clean. 🎉</p>
        </div>
      )}
    </div>
  );
}
