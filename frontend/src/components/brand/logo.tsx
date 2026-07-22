"use client";

import * as React from "react";

/**
 * PromptForge mark: a proper anvil (lucide 'anvil' silhouette) with a rising
 * wisp of "prompt smoke" + sparks, drawn in the brand violet→pink gradient.
 * Self-contained, theme-agnostic. The artwork is ~24×30, so size it by height
 * and let width follow (e.g. `h-9 w-auto`).
 */
export function Logo({ className }: { className?: string }) {
  const uid = React.useId().replace(/:/g, "");
  const id = `pf-${uid}`;
  return (
    <svg
      viewBox="0 0 24 30"
      className={className}
      fill="none"
      role="img"
      aria-label="PromptForge"
    >
      <defs>
        <linearGradient id={id} x1="2" y1="1" x2="22" y2="28" gradientUnits="userSpaceOnUse">
          <stop stopColor="#7c3aed" />
          <stop offset="1" stopColor="#db2777" />
        </linearGradient>
      </defs>

      {/* Rising prompt-smoke */}
      <g
        stroke={`url(#${id})`}
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      >
        <path d="M12 10c-2.6-2 2.6-3.2 0-5.4C10.9 3.5 13 2.7 12 1.4" />
        <path d="M14.4 8.6c1.9-1.4-1.4-2.4 0.5-4.2" opacity="0.8" />
      </g>
      <g fill={`url(#${id})`}>
        <circle cx="9" cy="4" r="0.55" />
        <circle cx="15.7" cy="2.7" r="0.6" />
        <circle cx="12.4" cy="1.3" r="0.5" />
      </g>

      {/* Anvil (lucide 'anvil' paths), shifted down to leave room for smoke */}
      <g
        transform="translate(0 6)"
        stroke={`url(#${id})`}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      >
        <path d="M7 10H6a4 4 0 0 1-4-4 1 1 0 0 1 1-1h4" />
        <path d="M7 5a1 1 0 0 1 1-1h13a1 1 0 0 1 1 1 7 7 0 0 1-7 7H8a1 1 0 0 1-1-1z" />
        <path d="M9 12v5" />
        <path d="M15 12v5" />
        <path d="M5 20a3 3 0 0 1 3-3h8a3 3 0 0 1 3 3 1 1 0 0 1-1 1H6a1 1 0 0 1-1-1" />
      </g>
    </svg>
  );
}
