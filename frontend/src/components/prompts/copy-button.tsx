"use client";

import { Check, Copy } from "lucide-react";
import * as React from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import { promptsApi } from "@/lib/prompts-api";

interface CopyButtonProps extends Omit<ButtonProps, "onClick"> {
  promptId: string;
  content: string;
  label?: string;
}

export function CopyButton({
  promptId,
  content,
  label = "Copy prompt",
  ...props
}: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false);

  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
    } catch {
      /* clipboard may be unavailable; still count the copy */
    }
    setCopied(true);
    // Fire-and-forget the server-side copy counter.
    void promptsApi.copy(promptId).catch(() => undefined);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <Button onClick={onCopy} {...props}>
      {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      {copied ? "Copied!" : label}
    </Button>
  );
}
