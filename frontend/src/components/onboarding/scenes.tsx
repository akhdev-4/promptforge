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

function Mascot({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 172" fill="none" className={className} aria-hidden>
      <defs>
        <linearGradient id="pf-shirt" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
      <ellipse cx="60" cy="166" rx="32" ry="5" fill="#00000012" />
      {/* legs */}
      <rect x="50" y="108" width="12" height="48" rx="6" fill="#3730a3" />
      <rect x="63" y="108" width="12" height="48" rx="6" fill="#3730a3" />
      {/* shoes */}
      <path d="M45 153 h15 v6 a3 3 0 0 1-3 3 h-16 v-2 q0-7 4-7z" fill="#111827" />
      <path d="M60 153 h15 v6 a3 3 0 0 1-3 3 h-16 v-2 q0-7 4-7z" fill="#111827" />
      {/* back arm */}
      <rect x="31" y="68" width="11" height="33" rx="5.5" fill="#7c3aed" />
      <circle cx="36.5" cy="101" r="5.5" fill="#f0c29a" />
      {/* torso */}
      <path d="M41 66 q19 -9 38 0 l4 44 q-23 7 -46 0 z" fill="url(#pf-shirt)" />
      {/* neck + head */}
      <rect x="53" y="50" width="14" height="13" rx="3" fill="#e3ab7d" />
      <circle cx="60" cy="38" r="18" fill="#f0c29a" />
      <circle cx="42.5" cy="39" r="3" fill="#f0c29a" />
      <circle cx="77.5" cy="39" r="3" fill="#f0c29a" />
      {/* hair */}
      <path
        d="M42 39 a18 18 0 0 1 36 0 q1-8-4-12 q-5 4-14 4 t-14-4 q-5 4-4 12z"
        fill="#2b2b31"
      />
      {/* face */}
      <circle cx="53" cy="39" r="2.2" fill="#2b3648" />
      <circle cx="67" cy="39" r="2.2" fill="#2b3648" />
      <path d="M54 46 q6 5 12 0" stroke="#2b3648" strokeWidth="2" fill="none" strokeLinecap="round" />
      {/* front arm holding the prompt cards */}
      <rect x="72" y="66" width="11" height="24" rx="5.5" fill="#7c3aed" transform="rotate(28 77 70)" />
      <rect x="78" y="70" width="10" height="22" rx="5" fill="#f0c29a" transform="rotate(-22 83 82)" />
      <g transform="rotate(-8 84 76)">
        <rect x="70" y="70" width="24" height="16" rx="2.5" fill="#fff" stroke="#e5e7eb" />
        <rect x="73" y="66" width="24" height="16" rx="2.5" fill="#fff" stroke="#e5e7eb" />
        <rect x="74" y="70" width="12" height="2.5" rx="1" fill="#7c3aed99" />
      </g>
    </svg>
  );
}

function LibraryScene() {
  return (
    <div className="relative flex h-full w-full items-center gap-3 px-5">
      {/* Character walks in and "delivers" the prompts */}
      <div className="pf-walk shrink-0">
        <div className="pf-float2">
          <Mascot className="h-44 w-auto" />
        </div>
      </div>
      {/* Prompts fly into organized shelves as the mascot arrives */}
      <div className="grid flex-1 grid-cols-2 gap-2.5">
        {Array.from({ length: 4 }).map((_, i) => (
          <div
            key={i}
            className="relative h-12 rounded-lg border-2 border-dashed border-primary/25"
          >
            <div
              className="pf-fly absolute inset-0 rounded-lg border border-border bg-card p-1.5 shadow-sm"
              style={{ animationDelay: `${0.8 + 0.18 * i}s` }}
            >
              <div className="h-1.5 w-8 rounded bg-primary/60" />
              <div className="mt-1 h-1 w-10 rounded bg-muted-foreground/30" />
            </div>
          </div>
        ))}
      </div>
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
