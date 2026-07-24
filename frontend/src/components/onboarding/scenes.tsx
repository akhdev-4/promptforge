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
    <svg viewBox="0 0 120 168" fill="none" className={className} aria-hidden>
      <defs>
        <linearGradient id="pf-shirt" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
      <ellipse cx="60" cy="162" rx="30" ry="5" fill="#00000012" />
      {/* joggers */}
      <path d="M49 104 h12 v38 q0 4-4 4 h-4 q-4 0-4-4z" fill="#334155" />
      <path d="M63 104 h12 v38 q0 4-4 4 h-4 q-4 0-4-4z" fill="#334155" />
      {/* sneakers */}
      <path d="M42 140 h15 v5 h-4 v3 h-15 q0-4 2-5z" fill="#f8fafc" stroke="#d1d5db" />
      <path d="M63 140 h15 v8 h-15 v-3 h-4 q0-5 4-5z" fill="#f8fafc" stroke="#d1d5db" />
      {/* back arm */}
      <rect x="30" y="66" width="12" height="32" rx="6" fill="#7c3aed" />
      <circle cx="36" cy="98" r="6" fill="#f4c9a0" />
      {/* hoodie */}
      <path d="M38 64 q22 -11 44 0 l3 44 q-25 8 -50 0 z" fill="url(#pf-shirt)" />
      <path d="M46 90 q14 5 28 0 l-2 12 q-12 4 -24 0z" fill="#00000012" />
      <path d="M45 60 q15 -12 30 0 q-5 9 -15 9 t-15 -9z" fill="#6d28d9" />
      <line x1="55" y1="66" x2="55" y2="80" stroke="#fff" strokeWidth="1.6" />
      <circle cx="55" cy="81" r="1.4" fill="#fff" />
      <line x1="65" y1="66" x2="65" y2="80" stroke="#fff" strokeWidth="1.6" />
      <circle cx="65" cy="81" r="1.4" fill="#fff" />
      {/* neck + head (bigger, younger) */}
      <rect x="53" y="45" width="14" height="12" rx="3" fill="#e6b184" />
      <circle cx="60" cy="32" r="21" fill="#f4c9a0" />
      <circle cx="39.5" cy="33" r="3.2" fill="#f4c9a0" />
      <circle cx="80.5" cy="33" r="3.2" fill="#f4c9a0" />
      {/* tousled hair */}
      <path
        d="M39 33 q-1-13 8-18 q3 4 8 3 q4 3 9 0 q4 2 8-1 q9 6 9 16 q-4-7-10-8 q-3 3-8 2 q-5 2-9-1 q-6 2-9 7 q-2-2-5 0z"
        fill="#4a3b2f"
      />
      {/* big eyes + smile */}
      <circle cx="52" cy="33" r="2.8" fill="#2b3648" />
      <circle cx="53" cy="32" r="0.9" fill="#fff" />
      <circle cx="68" cy="33" r="2.8" fill="#2b3648" />
      <circle cx="69" cy="32" r="0.9" fill="#fff" />
      <path d="M52 41 q8 6 16 0" stroke="#2b3648" strokeWidth="2.2" fill="none" strokeLinecap="round" />
      {/* front arm holding the prompt cards */}
      <rect x="71" y="64" width="12" height="24" rx="6" fill="#7c3aed" transform="rotate(26 77 68)" />
      <rect x="78" y="70" width="10" height="20" rx="5" fill="#f4c9a0" transform="rotate(-24 83 82)" />
      <g transform="rotate(-8 84 74)">
        <rect x="70" y="68" width="24" height="16" rx="2.5" fill="#fff" stroke="#e5e7eb" />
        <rect x="73" y="64" width="24" height="16" rx="2.5" fill="#fff" stroke="#e5e7eb" />
        <rect x="76" y="68" width="12" height="2.4" rx="1" fill="#7c3aed99" />
      </g>
    </svg>
  );
}

const LIBRARY_CARDS = [
  { title: "Glass Login UI", desc: "Glassmorphism sign-in" },
  { title: "Stripe Checkout", desc: "Payment flow" },
  { title: "Ghibli Portrait", desc: "Anime photo style" },
  { title: "JWT Auth API", desc: "Login + refresh" },
];

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
        {LIBRARY_CARDS.map((c, i) => (
          <div
            key={c.title}
            className="relative h-14 rounded-lg border-2 border-dashed border-primary/25"
          >
            <div
              className="pf-fly absolute inset-0 rounded-lg border border-border bg-card p-2 shadow-sm"
              style={{ animationDelay: `${0.8 + 0.18 * i}s` }}
            >
              <div className="flex items-center gap-1">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span className="truncate text-[11px] font-semibold text-foreground">
                  {c.title}
                </span>
              </div>
              <p className="mt-0.5 truncate text-[9px] leading-tight text-muted-foreground">
                {c.desc}
              </p>
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
