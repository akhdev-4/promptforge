"use client";

import { Loader2, Send } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";
import { useAddVersion } from "@/hooks/use-prompts";
import { ApiError } from "@/lib/api";

/**
 * Lets someone who isn't the owner add a version to an open prompt. The owner
 * uses the Edit page instead, which also covers metadata.
 */
export function ContributeVersion({ promptId }: { promptId: string }) {
  const addVersion = useAddVersion(promptId);
  const toast = useToast();
  const [open, setOpen] = React.useState(false);
  const [content, setContent] = React.useState("");
  const [summary, setSummary] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);

  const submit = async () => {
    setError(null);
    try {
      await addVersion.mutateAsync({
        content: content.trim(),
        change_summary: summary.trim() || undefined,
      });
      toast.success("Version added — the history now credits you.");
      setContent("");
      setSummary("");
      setOpen(false);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Couldn't add your version.");
    }
  };

  if (!open) {
    return (
      <Card className="border-dashed">
        <CardContent className="flex flex-wrap items-center justify-between gap-3 p-4">
          <p className="text-sm text-muted-foreground">
            This prompt is open to contributions — improve it and your version will
            be credited to you.
          </p>
          <Button size="sm" variant="outline" onClick={() => setOpen(true)}>
            Suggest a new version
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Add a new version</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-1.5">
          <Label htmlFor="contrib-content">Prompt content</Label>
          <Textarea
            id="contrib-content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="min-h-48 font-mono text-xs"
            placeholder="Paste the improved prompt in full…"
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="contrib-summary">What changed? (optional)</Label>
          <Input
            id="contrib-summary"
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            maxLength={500}
            placeholder="e.g. Tightened the constraints and added an output format"
          />
        </div>
        {error && <p className="text-xs text-destructive">{error}</p>}
        <div className="flex gap-2">
          <Button
            size="sm"
            onClick={submit}
            disabled={addVersion.isPending || !content.trim()}
          >
            {addVersion.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            Add version
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setOpen(false)}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
