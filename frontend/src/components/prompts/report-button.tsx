"use client";

import { Check, Flag, Loader2 } from "lucide-react";
import * as React from "react";
import { createPortal } from "react-dom";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useReportPrompt } from "@/hooks/use-community";

export function ReportButton({ promptId }: { promptId: string }) {
  const [open, setOpen] = React.useState(false);
  const [reason, setReason] = React.useState("");
  const [done, setDone] = React.useState(false);
  const report = useReportPrompt(promptId);
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const submit = async () => {
    if (!reason.trim() || report.isPending) return;
    await report.mutateAsync(reason.trim());
    setDone(true);
    setTimeout(() => {
      setOpen(false);
      setDone(false);
      setReason("");
    }, 1600);
  };

  return (
    <>
      <Button
        variant="outline"
        onClick={() => setOpen(true)}
        title="Report this prompt to moderators"
      >
        <Flag className="h-4 w-4" /> Report
      </Button>

      {mounted &&
        open &&
        createPortal(
          <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
            <div
              className="absolute inset-0 bg-black/50"
              onClick={() => !report.isPending && setOpen(false)}
            />
            <div className="relative w-full max-w-md rounded-2xl border border-border bg-card p-5 shadow-2xl">
              {done ? (
                <div className="flex flex-col items-center gap-2 py-6 text-center">
                  <Check className="h-8 w-8 text-success" />
                  <p className="font-medium">Thanks — reported to moderators.</p>
                </div>
              ) : (
                <>
                  <h3 className="flex items-center gap-2 text-base font-semibold">
                    <Flag className="h-4 w-4 text-destructive" /> Report this prompt
                  </h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    Tell us what&rsquo;s wrong (spam, offensive, broken, plagiarised…).
                  </p>
                  <Textarea
                    className="mt-3"
                    rows={3}
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Reason for reporting…"
                  />
                  <div className="mt-3 flex justify-end gap-2">
                    <Button variant="ghost" onClick={() => setOpen(false)}>
                      Cancel
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={submit}
                      disabled={!reason.trim() || report.isPending}
                    >
                      {report.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                      Submit report
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
