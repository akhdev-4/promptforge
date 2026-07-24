"use client";

import {
  BarChart3,
  Blocks,
  LayoutDashboard,
  Library,
  Rocket,
  Sparkles,
  X,
  type LucideIcon,
} from "lucide-react";
import * as React from "react";
import { createPortal } from "react-dom";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const STORAGE_KEY = "pf_onboarding_v1_seen";

interface Step {
  icon: LucideIcon;
  title: string;
  body: React.ReactNode;
}

const STEPS: Step[] = [
  {
    icon: Sparkles,
    title: "Welcome to PromptForge",
    body: (
      <>
        Think <strong>“GitHub for AI prompts.”</strong> It&rsquo;s a home for
        production-tested prompts — <strong>find</strong> proven ones,{" "}
        <strong>run</strong> them to see real output, and <strong>build</strong> whole apps
        from them. Here&rsquo;s a 30-second tour of the sections in the sidebar.
      </>
    ),
  },
  {
    icon: LayoutDashboard,
    title: "Dashboard",
    body: (
      <>
        Your home base. See what&rsquo;s <strong>trending</strong> (most-copied prompts), the{" "}
        <strong>latest</strong> additions, and quick stats — a pulse of what&rsquo;s useful
        right now.
      </>
    ),
  },
  {
    icon: Library,
    title: "Library",
    body: (
      <>
        The whole prompt collection. Switch between two lanes —{" "}
        <strong>App Development</strong> and <strong>AI &amp; Creative</strong> — browse by
        category, save <strong>Favorites</strong>, group them into{" "}
        <strong>Collections</strong>, and <strong>rate</strong> the best ones. Open any prompt
        and hit <strong>Run</strong> in the Playground to see its real output (text or a
        generated image).
      </>
    ),
  },
  {
    icon: Blocks,
    title: "Build",
    body: (
      <>
        Assemble applications from proven prompts:{" "}
        <strong>Projects → Modules → Components</strong>. And create <strong>Teams</strong>{" "}
        to share <strong>private</strong> prompts with a group — only members can see them.
      </>
    ),
  },
  {
    icon: BarChart3,
    title: "Insights",
    body: (
      <>
        Track engagement with <strong>Analytics</strong> — trending, growth, top contributors
        — and manage your profile and appearance in <strong>Settings</strong>.
      </>
    ),
  },
  {
    icon: Rocket,
    title: "You’re all set",
    body: (
      <>
        One tip: tap the <strong>sparkle button</strong> (bottom-right) to open{" "}
        <strong>Stringer</strong> — describe (or <strong>speak</strong>) what you need and it
        finds the closest prompts. Enjoy building!
      </>
    ),
  },
];

export function OnboardingTour() {
  const user = useAuthStore((s) => s.user);
  const [mounted, setMounted] = React.useState(false);
  const [open, setOpen] = React.useState(false);
  const [step, setStep] = React.useState(0);

  React.useEffect(() => {
    setMounted(true);
    const openGuide = () => {
      setStep(0);
      setOpen(true);
    };
    window.addEventListener("pf:open-guide", openGuide);
    return () => window.removeEventListener("pf:open-guide", openGuide);
  }, []);

  // Auto-open once for first-time users.
  React.useEffect(() => {
    if (mounted && user && localStorage.getItem(STORAGE_KEY) !== "1") {
      setStep(0);
      setOpen(true);
    }
  }, [mounted, user]);

  const finish = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setOpen(false);
  };

  if (!mounted || !user || !open) return null;

  const s = STEPS[step]!;
  const Icon = s.icon;
  const isLast = step === STEPS.length - 1;

  return createPortal(
    <div className="fixed inset-0 z-[80] flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={finish} />
      <div className="relative w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card shadow-2xl">
        <button
          onClick={finish}
          aria-label="Skip"
          className="absolute right-3 top-3 rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Header band */}
        <div className="flex flex-col items-center gap-3 bg-gradient-to-b from-primary/10 to-transparent px-6 pb-4 pt-8 text-center">
          <span
            key={`icon-${step}`}
            className="pf-onb-pop flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-md"
          >
            <Icon className="h-7 w-7" />
          </span>
        </div>

        {/* Content */}
        <div key={`body-${step}`} className="pf-onb-in space-y-2 px-6 pb-2 text-center">
          <h2 className="text-xl font-semibold tracking-tight">{s.title}</h2>
          <p className="text-sm leading-relaxed text-muted-foreground">{s.body}</p>
        </div>

        {/* Progress dots */}
        <div className="flex items-center justify-center gap-1.5 py-4">
          {STEPS.map((_, i) => (
            <span
              key={i}
              className={cn(
                "h-1.5 rounded-full transition-all",
                i === step ? "w-5 bg-primary" : "w-1.5 bg-muted-foreground/30",
              )}
            />
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-border p-4">
          {step > 0 ? (
            <Button variant="ghost" size="sm" onClick={() => setStep((v) => v - 1)}>
              Back
            </Button>
          ) : (
            <Button variant="ghost" size="sm" onClick={finish}>
              Skip
            </Button>
          )}
          <span className="text-xs text-muted-foreground">
            {step + 1} / {STEPS.length}
          </span>
          <Button size="sm" onClick={() => (isLast ? finish() : setStep((v) => v + 1))}>
            {isLast ? "Get started" : "Next"}
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  );
}
