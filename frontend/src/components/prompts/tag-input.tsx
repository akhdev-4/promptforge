"use client";

import { X } from "lucide-react";
import * as React from "react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  suggestions?: string[];
}

export function TagInput({ value, onChange, placeholder, suggestions = [] }: TagInputProps) {
  const [draft, setDraft] = React.useState("");

  const add = (raw: string) => {
    const tag = raw.trim().replace(/,$/, "");
    if (!tag) return;
    const exists = value.some((t) => t.toLowerCase() === tag.toLowerCase());
    if (!exists && value.length < 20) onChange([...value, tag]);
    setDraft("");
  };

  const remove = (tag: string) => onChange(value.filter((t) => t !== tag));

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      add(draft);
    } else if (e.key === "Backspace" && !draft && value.length) {
      remove(value[value.length - 1]!);
    }
  };

  const available = suggestions.filter(
    (s) => !value.some((t) => t.toLowerCase() === s.toLowerCase()),
  );

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "flex min-h-10 flex-wrap items-center gap-1.5 rounded-lg border border-input bg-background px-2 py-1.5",
          "focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-1 focus-within:ring-offset-background",
        )}
      >
        {value.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
          >
            {tag}
            <button
              type="button"
              onClick={() => remove(tag)}
              className="rounded-full hover:bg-primary/20"
              aria-label={`Remove ${tag}`}
            >
              <X className="h-3 w-3" />
            </button>
          </span>
        ))}
        <Input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          onBlur={() => add(draft)}
          placeholder={value.length ? "" : (placeholder ?? "Add tags…")}
          className="h-6 flex-1 border-0 p-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
        />
      </div>
      {available.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {available.slice(0, 8).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => add(s)}
              className="rounded-md border border-border px-2 py-0.5 text-xs text-muted-foreground hover:border-primary/40 hover:text-primary"
            >
              + {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
