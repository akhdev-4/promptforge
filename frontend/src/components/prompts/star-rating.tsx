"use client";

import { Star } from "lucide-react";
import * as React from "react";

import { cn } from "@/lib/utils";

interface StarRatingProps {
  /** Current value (0–5). For interactive use, the user's own rating. */
  value: number;
  /** Read-only display (e.g. a prompt's average). */
  readOnly?: boolean;
  onRate?: (stars: number) => void;
  size?: "sm" | "md" | "lg";
  className?: string;
}

const SIZES = { sm: "h-3.5 w-3.5", md: "h-5 w-5", lg: "h-7 w-7" } as const;

/**
 * Five-star widget. Read-only mode renders partial fills (e.g. 4.3 → 4.3 stars)
 * via a clipped overlay; interactive mode lets the user click 1–5 with a hover
 * preview.
 */
export function StarRating({
  value,
  readOnly = false,
  onRate,
  size = "md",
  className,
}: StarRatingProps) {
  const [hover, setHover] = React.useState<number | null>(null);
  const cls = SIZES[size];
  const shown = hover ?? value;

  if (readOnly) {
    return (
      <span className={cn("inline-flex items-center gap-0.5", className)} aria-label={`${value} out of 5`}>
        {[1, 2, 3, 4, 5].map((i) => {
          const fill = Math.max(0, Math.min(1, value - (i - 1))); // 0..1 for this star
          return (
            <span key={i} className="relative inline-block">
              <Star className={cn(cls, "text-muted-foreground/30")} />
              <span
                className="absolute inset-0 overflow-hidden"
                style={{ width: `${fill * 100}%` }}
              >
                <Star className={cn(cls, "fill-amber-400 text-amber-400")} />
              </span>
            </span>
          );
        })}
      </span>
    );
  }

  return (
    <span
      className={cn("inline-flex items-center gap-0.5", className)}
      onMouseLeave={() => setHover(null)}
      role="radiogroup"
      aria-label="Rate this prompt"
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <button
          key={i}
          type="button"
          role="radio"
          aria-checked={value === i}
          aria-label={`${i} star${i === 1 ? "" : "s"}`}
          onMouseEnter={() => setHover(i)}
          onClick={() => onRate?.(i)}
          className="rounded transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <Star
            className={cn(
              cls,
              i <= shown ? "fill-amber-400 text-amber-400" : "text-muted-foreground/40",
            )}
          />
        </button>
      ))}
    </span>
  );
}
