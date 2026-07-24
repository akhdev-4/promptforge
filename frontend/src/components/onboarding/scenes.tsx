"use client";

import { Rocket, Sparkles } from "lucide-react";
import type * as React from "react";

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

/** Young developer at a workspace: thick black hair, hoodie, laptop. */
function Developer({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 150 185" fill="none" className={className} aria-hidden>
      <defs>
        <linearGradient id="pf-hood" x1="0" y1="0" x2="0" y2="1">
          <stop stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
      </defs>
      {/* hoodie shoulders */}
      <path d="M18 185 q0-52 57-52 t57 52 z" fill="url(#pf-hood)" />
      {/* hood collar */}
      <path d="M52 140 q23 -14 46 0 q-7 12 -23 12 t-23 -12z" fill="#6d28d9" />
      {/* drawstrings */}
      <line x1="66" y1="146" x2="66" y2="162" stroke="#fff" strokeWidth="2" />
      <circle cx="66" cy="163" r="1.6" fill="#fff" />
      <line x1="84" y1="146" x2="84" y2="162" stroke="#fff" strokeWidth="2" />
      <circle cx="84" cy="163" r="1.6" fill="#fff" />
      {/* neck */}
      <rect x="66" y="118" width="18" height="16" rx="4" fill="#e2ac7c" />
      {/* head + ears */}
      <circle cx="75" cy="92" r="27" fill="#f0c19a" />
      <circle cx="48" cy="93" r="4" fill="#f0c19a" />
      <circle cx="102" cy="93" r="4" fill="#f0c19a" />
      {/* thick black hair */}
      <path
        d="M48 92 q-3-30 15-36 q6 6 12 5 q7 4 15-1 q7 3 12-2 q12 9 11 34 q-6-12-15-13 q-5 4-13 3 q-8 3-14-2 q-9 3-13 12 q-4-2-8 0z"
        fill="#17171c"
      />
      <path d="M52 66 q10-10 24-8" stroke="#2c2c34" strokeWidth="3" fill="none" strokeLinecap="round" />
      {/* brows + expressive eyes */}
      <path d="M58 84 q6-3 11 0" stroke="#17171c" strokeWidth="2.2" fill="none" strokeLinecap="round" />
      <path d="M84 84 q6-3 11 0" stroke="#17171c" strokeWidth="2.2" fill="none" strokeLinecap="round" />
      <circle cx="63" cy="92" r="3.4" fill="#22303f" />
      <circle cx="64.5" cy="90.5" r="1.1" fill="#fff" />
      <circle cx="89" cy="92" r="3.4" fill="#22303f" />
      <circle cx="90.5" cy="90.5" r="1.1" fill="#fff" />
      {/* friendly smile */}
      <path d="M64 104 q11 8 22 0" stroke="#b5714b" strokeWidth="2.6" fill="none" strokeLinecap="round" />
      {/* laptop on the desk */}
      <rect x="34" y="168" width="82" height="10" rx="3" fill="#cbd5e1" />
      <path d="M42 168 v-22 a3 3 0 0 1 3-3 h60 a3 3 0 0 1 3 3 v22z" fill="#1e293b" />
      <rect x="48" y="150" width="48" height="14" rx="2" fill="#334155" />
      <rect x="51" y="153" width="20" height="2.4" rx="1" fill="#8b5cf6" />
      <rect x="51" y="158" width="30" height="2.4" rx="1" fill="#64748b" />
    </svg>
  );
}

const LIBRARY_CARDS = [
  { title: "Login UI", desc: "Glass sign-in", dot: "#7c3aed", dx: 300, dy: -40 },
  { title: "Stripe API", desc: "Payment flow", dot: "#3b82f6", dx: 290, dy: 40 },
  { title: "Ghibli Art", desc: "Anime style", dot: "#ec4899", dx: 320, dy: 10 },
];

// Book spines that "materialize" on the shelves as cards arrive.
const BOOK_PALETTE = ["#6366f1", "#8b5cf6", "#7c3aed", "#a78bfa", "#3b82f6", "#818cf8", "#ec4899"];
function shelfBooks(seed: number, count = 9) {
  return Array.from({ length: count }, (_, i) => ({
    h: 30 + ((i * 7 + seed * 13) % 22),
    c: BOOK_PALETTE[(i + seed) % BOOK_PALETTE.length]!,
    // staggered so the shelf fills left-to-right in time with the flying cards
    delay: 0.15 * i + seed * 0.4,
  }));
}

function Shelf({ seed }: { seed: number }) {
  return (
    <div className="relative flex flex-1 items-end justify-center gap-[3px] border-b-4 border-[#8a5a34] px-2 pb-1">
      {shelfBooks(seed).map((b, i) => (
        <div
          key={i}
          className="pf-book-rise w-2.5 rounded-t-sm"
          style={{
            height: `${b.h}px`,
            background: b.c,
            boxShadow: "inset -2px 0 0 rgba(0,0,0,0.15)",
            animationDelay: `${b.delay}s`,
          }}
        />
      ))}
    </div>
  );
}

function LibraryScene() {
  return (
    <div className="relative h-full w-full overflow-hidden">
      {/* Developer at the workspace */}
      <div className="pf-walk absolute bottom-0 left-2">
        <div className="pf-float2">
          <Developer className="h-44 w-auto" />
        </div>
      </div>

      {/* Prompt cards the dev sends toward the shelf */}
      {LIBRARY_CARDS.map((c, i) => (
        <div
          key={c.title}
          className="pf-card-send absolute z-10 w-24 rounded-lg border border-border bg-card p-1.5 shadow-md"
          style={
            {
              left: "128px",
              top: `${44 + i * 46}px`,
              "--dx": `${c.dx}px`,
              "--dy": `${c.dy}px`,
              animationDelay: `${i * 0.7}s`,
            } as React.CSSProperties
          }
        >
          <div className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: c.dot }} />
            <span className="truncate text-[10px] font-semibold text-foreground">{c.title}</span>
          </div>
          <p className="truncate text-[8px] leading-tight text-muted-foreground">{c.desc}</p>
        </div>
      ))}

      {/* Wooden bookshelf that fills with organized books */}
      <div className="absolute right-4 top-8 h-[184px] w-[372px]">
        {/* soft violet glow when the library is organized */}
        <div
          className="pf-shelf-glow absolute -inset-3 rounded-2xl"
          style={{ background: "radial-gradient(circle, rgba(139,92,246,0.45), transparent 70%)" }}
        />
        <div
          className="relative flex h-full flex-col gap-1.5 rounded-xl p-2"
          style={{
            background: "linear-gradient(#caa274,#b3854f)",
            boxShadow: "inset 0 0 0 4px #a06a3f, 0 6px 16px rgba(0,0,0,0.13)",
          }}
        >
          <div
            className="absolute rounded-md"
            style={{ inset: "8px", background: "linear-gradient(#e2c49a,#d3ac7f)" }}
          />
          <Shelf seed={0} />
          <Shelf seed={3} />
        </div>
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
