"use client";

import * as React from "react";

/**
 * PromptForge mark: an anvil with a rising wisp of "prompt smoke", in the brand
 * violet→pink gradient. Self-contained (its own gradient), so it looks right on
 * any background in light or dark mode. Size it via className (h-/w-).
 */
export function Logo({ className }: { className?: string }) {
  const uid = React.useId().replace(/:/g, "");
  const grad = `pf-anvil-${uid}`;
  return (
    <svg
      viewBox="0 0 48 48"
      className={className}
      fill="none"
      role="img"
      aria-label="PromptForge"
    >
      <defs>
        <linearGradient id={grad} x1="6" y1="4" x2="42" y2="44" gradientUnits="userSpaceOnUse">
          <stop stopColor="#7c3aed" />
          <stop offset="1" stopColor="#db2777" />
        </linearGradient>
      </defs>

      {/* Rising "smoke of prompts" */}
      <path
        d="M24 14c-3-2.5 3-4-0.5-7.4C21.6 4.6 25 3 24 1"
        stroke={`url(#${grad})`}
        strokeWidth="1.9"
        strokeLinecap="round"
      />

      {/* Anvil */}
      <g fill={`url(#${grad})`}>
        <path d="M11 17 4 20l7 3z" /> {/* horn */}
        <path d="M12 16h26a3 3 0 0 1 3 3v1a3 3 0 0 1-3 3H12a3 3 0 0 1-3-3v-1a3 3 0 0 1 3-3z" />
        <path d="M21 23h6v7h-6z" /> {/* waist */}
        <path d="M12 30h24l2.5 5h-29z" /> {/* base */}
      </g>
    </svg>
  );
}
