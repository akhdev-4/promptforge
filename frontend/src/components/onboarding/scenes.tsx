"use client";

import { Rocket, Sparkles } from "lucide-react";

/** Small, self-contained SVG/CSS "live preview" scenes for the onboarding tour. */

function Welcome() {
  const tokens = [
    { c: "{ }", x: "14%", y: "22%", d: 0 },
    { c: "</>", x: "76%", y: "18%", d: 0.4 },
    { c: '" "', x: "20%", y: "70%", d: 0.8 },
    { c: "#tag", x: "72%", y: "68%", d: 0.2 },
    { c: "[ ]", x: "48%", y: "12%", d: 0.6 },
  ];
  return (
    <div className="relative h-full w-full overflow-hidden">
      {tokens.map((t) => (
        <span
          key={t.c}
          className="pf-float2 absolute font-mono text-sm font-semibold text-primary/50"
          style={{ left: t.x, top: t.y, animationDelay: `${t.d}s` }}
        >
          {t.c}
        </span>
      ))}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <div className="pf-float2 flex h-20 w-20 items-center justify-center rounded-[1.4rem] bg-gradient-to-br from-violet-500 to-pink-500 text-white shadow-lg">
          <Sparkles className="h-9 w-9" />
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const bars = [42, 64, 52, 82, 60, 74];
  return (
    <div className="relative h-full w-full overflow-hidden px-6 pb-5 pt-6">
      <svg className="absolute inset-x-6 top-4 h-14 w-[calc(100%-3rem)]" viewBox="0 0 200 50" fill="none">
        <path
          className="pf-draw"
          d="M2 42 L44 34 L86 38 L128 18 L170 22 L198 6"
          stroke="#8b5cf6"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle className="pf-twinkle2" cx="198" cy="6" r="4" fill="#ec4899" />
      </svg>
      <div className="flex h-full items-end justify-center gap-3">
        {bars.map((h, i) => (
          <div
            key={i}
            className="pf-grow w-6 rounded-t bg-gradient-to-t from-primary to-violet-400"
            style={{ height: `${h}%`, animationDelay: `${0.08 * i}s` }}
          />
        ))}
      </div>
    </div>
  );
}

function LibraryScene() {
  return (
    <div className="relative grid h-full w-full grid-cols-3 content-center gap-2.5 px-6 py-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="relative h-14 rounded-lg border-2 border-dashed border-primary/25"
        >
          <div
            className="pf-fly absolute inset-0 rounded-lg border border-border bg-card p-2 shadow-sm"
            style={{ animationDelay: `${0.12 * i}s` }}
          >
            <div className="h-1.5 w-9 rounded bg-primary/60" />
            <div className="mt-1.5 h-1 w-11 rounded bg-muted-foreground/30" />
            <div className="mt-1 h-1 w-7 rounded bg-muted-foreground/20" />
          </div>
        </div>
      ))}
    </div>
  );
}

function Build() {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-2.5">
      <div className="pf-drop flex gap-1.5" style={{ animationDelay: "0.3s" }}>
        {[0, 1, 2].map((i) => (
          <div key={i} className="h-6 w-10 rounded-md bg-pink-400/80 shadow-sm" />
        ))}
      </div>
      <div className="pf-drop flex gap-2" style={{ animationDelay: "0.15s" }}>
        {[0, 1].map((i) => (
          <div key={i} className="h-7 w-20 rounded-md bg-violet-400/80 shadow-sm" />
        ))}
      </div>
      <div
        className="pf-drop h-9 w-44 rounded-md bg-gradient-to-r from-primary to-primary/70 shadow-sm"
        style={{ animationDelay: "0s" }}
      />
    </div>
  );
}

function Insights() {
  return (
    <div className="relative h-full w-full overflow-hidden p-5">
      <svg className="h-full w-full" viewBox="0 0 240 120" fill="none" preserveAspectRatio="none">
        <defs>
          <linearGradient id="pf-ins" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#8b5cf6" stopOpacity="0.35" />
            <stop offset="1" stopColor="#8b5cf6" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d="M6 104 C 46 96, 66 60, 104 66 S 176 26, 234 12 L234 118 L6 118 Z"
          fill="url(#pf-ins)"
        />
        <path
          className="pf-draw"
          d="M6 104 C 46 96, 66 60, 104 66 S 176 26, 234 12"
          stroke="#8b5cf6"
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle className="pf-twinkle2" cx="104" cy="66" r="4" fill="#ec4899" />
        <circle
          className="pf-twinkle2"
          cx="234"
          cy="12"
          r="4"
          fill="#ec4899"
          style={{ animationDelay: "0.6s" }}
        />
      </svg>
    </div>
  );
}

function Finish() {
  const sparks = [
    { x: "24%", y: "26%", d: 0 },
    { x: "74%", y: "22%", d: 0.3 },
    { x: "20%", y: "68%", d: 0.6 },
    { x: "78%", y: "66%", d: 0.15 },
    { x: "50%", y: "16%", d: 0.45 },
  ];
  return (
    <div className="relative flex h-full w-full items-center justify-center overflow-hidden">
      {sparks.map((s, i) => (
        <Sparkles
          key={i}
          className="pf-twinkle2 absolute h-4 w-4 text-amber-400"
          style={{ left: s.x, top: s.y, animationDelay: `${s.d}s` }}
        />
      ))}
      <div className="pf-onb-pop flex h-20 w-20 items-center justify-center rounded-[1.4rem] bg-gradient-to-br from-primary to-violet-500 text-white shadow-lg">
        <Rocket className="pf-float2 h-9 w-9" />
      </div>
    </div>
  );
}

const SCENES = [Welcome, Dashboard, LibraryScene, Build, Insights, Finish];

export function OnboardingScene({ index }: { index: number }) {
  const Scene = SCENES[index] ?? Welcome;
  return <Scene />;
}
