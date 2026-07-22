"use client";

import { Loader2, Play, Send, Sparkles, X } from "lucide-react";
import Link from "next/link";
import * as React from "react";
import { createPortal } from "react-dom";

import { Badge } from "@/components/ui/badge";
import { useCategoryTree } from "@/hooks/use-taxonomy";
import { promptsApi } from "@/lib/prompts-api";
import { promptTypeLabels } from "@/lib/prompt-meta";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";
import type { PromptSummary } from "@/types";

// --- Lightweight intent parsing (no external LLM needed) --------------------
const STOP = new Set([
  "i", "a", "an", "the", "to", "for", "of", "and", "or", "need", "want", "looking",
  "find", "show", "me", "give", "get", "some", "any", "that", "this", "can", "you",
  "help", "please", "with", "how", "do", "my", "use", "using", "like", "would",
  "should", "is", "are", "best", "good", "one", "prompt", "prompts", "about", "on",
  "in", "it", "as", "so", "what", "which", "where", "make", "create", "build",
  "something", "thing", "please", "app", "website", "site", "page",
]);

const CREATIVE_HINTS = new Set([
  "image", "images", "photo", "photos", "picture", "pictures", "portrait", "avatar",
  "logo", "sticker", "stickers", "anime", "ghibli", "illustration", "art", "artwork",
  "headshot", "figurine", "wallpaper", "poster", "cartoon", "drawing", "painting",
  "watercolor", "edit", "editing", "restore", "colorize", "selfie", "instagram",
  "thumbnail", "cyberpunk", "polaroid", "diorama",
]);

const DEV_HINTS = new Set([
  "api", "apis", "login", "auth", "authentication", "jwt", "database", "sql", "schema",
  "react", "nextjs", "fastapi", "backend", "frontend", "endpoint", "endpoints",
  "component", "components", "checkout", "cart", "dashboard", "ui", "code", "python",
  "typescript", "stripe", "webhook", "webhooks", "migration", "test", "tests",
  "deploy", "deployment", "docker", "admin", "form", "table", "crud", "oauth",
  "password", "search", "navbar", "header", "footer", "modal",
]);

function extractKeywords(text: string): string[] {
  const words = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/);
  const seen = new Set<string>();
  const out: string[] = [];
  for (const w of words) {
    if (w.length >= 2 && !STOP.has(w) && !seen.has(w)) {
      seen.add(w);
      out.push(w);
    }
  }
  return out.slice(0, 5);
}

function detectLane(words: string[]): "creative" | "dev" | "all" {
  let c = 0;
  let d = 0;
  for (const w of words) {
    if (CREATIVE_HINTS.has(w)) c++;
    if (DEV_HINTS.has(w)) d++;
  }
  if (c > d && c > 0) return "creative";
  if (d > 0) return "dev";
  return "all";
}

interface Msg {
  id: string;
  role: "bot" | "user";
  text: string;
  results?: PromptSummary[];
}

const GREETINGS = new Set(["hi", "hello", "hey", "yo", "hola", "sup", "thanks", "thank"]);
const SUGGESTIONS = ["Login page UI", "Stripe checkout", "Anime portrait", "Product API"];

let msgSeq = 0;
const nextId = () => `m${++msgSeq}`;

export function PromptAssistant() {
  const user = useAuthStore((s) => s.user);
  const { data: tree } = useCategoryTree();
  const creativeRootId = React.useMemo(
    () => (tree ?? []).find((n) => n.name === "Creative & Media")?.id,
    [tree],
  );

  const [mounted, setMounted] = React.useState(false);
  const [open, setOpen] = React.useState(false);
  const [input, setInput] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [messages, setMessages] = React.useState<Msg[]>([]);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => setMounted(true), []);

  // Greet once, personalized, when first opened.
  React.useEffect(() => {
    if (open && messages.length === 0 && user) {
      setMessages([
        {
          id: nextId(),
          role: "bot",
          text: `Hi ${user.full_name?.split(" ")[0] ?? user.username ?? "there"}! I'm Stringer. Tell me what you're building or the kind of prompt you need — a login page, a Stripe webhook, an anime portrait — and I'll pull the closest matches so you don't have to scroll.`,
        },
      ]);
    }
  }, [open, messages.length, user]);

  React.useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  const laneFilter = (lane: "creative" | "dev" | "all") => {
    if (!creativeRootId) return {};
    if (lane === "creative") return { category_id: creativeRootId };
    if (lane === "dev") return { exclude_category_id: creativeRootId };
    return {};
  };

  const search = async (
    keywords: string[],
    filter: { category_id?: string; exclude_category_id?: string },
  ): Promise<PromptSummary[]> => {
    const pages = await Promise.all(
      keywords.map((k) =>
        promptsApi.list({ q: k, size: 6, sort: "most_copied", ...filter }).catch(() => ({
          items: [] as PromptSummary[],
        })),
      ),
    );
    // Rank by how many keywords surfaced each prompt, then by popularity.
    const score = new Map<string, { hits: number; prompt: PromptSummary }>();
    for (const page of pages) {
      for (const p of page.items) {
        const e = score.get(p.id) ?? { hits: 0, prompt: p };
        e.hits += 1;
        score.set(p.id, e);
      }
    }
    return [...score.values()]
      .sort((a, b) => b.hits - a.hits || b.prompt.copies_count - a.prompt.copies_count)
      .slice(0, 4)
      .map((e) => e.prompt);
  };

  const respond = async (text: string) => {
    const clean = text.trim();
    if (!clean || busy) return;
    setMessages((m) => [...m, { id: nextId(), role: "user", text: clean }]);
    setInput("");
    setBusy(true);

    const words = clean.toLowerCase().replace(/[^a-z0-9\s]/g, " ").split(/\s+/);
    const keywords = extractKeywords(clean);

    // Pure greeting / no searchable terms.
    if (keywords.length === 0) {
      const isGreeting = words.some((w) => GREETINGS.has(w));
      setMessages((m) => [
        ...m,
        {
          id: nextId(),
          role: "bot",
          text: isGreeting
            ? "Hey! Describe the prompt you're after — mention a feature or technology (e.g. “passwordless login”, “product catalog API”, “Ghibli portrait”) and I'll find it."
            : "Tell me a bit more — a feature, technology, or style works best (e.g. “cart drawer”, “Stripe checkout”, “anime avatar”).",
        },
      ]);
      setBusy(false);
      return;
    }

    const lane = detectLane(words);
    let results = await search(keywords, laneFilter(lane));
    // Broaden if a scoped lane found nothing.
    if (results.length === 0 && lane !== "all") {
      results = await search(keywords, {});
    }

    if (results.length === 0) {
      setMessages((m) => [
        ...m,
        {
          id: nextId(),
          role: "bot",
          text: `I couldn't find a close match for “${clean}”. Try naming a specific feature or technology — like “login”, “checkout”, “dashboard”, or “portrait”.`,
        },
      ]);
    } else {
      const laneNote =
        lane === "creative"
          ? " from the AI & Creative library"
          : lane === "dev"
            ? " from the App Development library"
            : "";
      setMessages((m) => [
        ...m,
        {
          id: nextId(),
          role: "bot",
          text: `Here ${results.length === 1 ? "is" : "are"} ${results.length} prompt${
            results.length === 1 ? "" : "s"
          }${laneNote} that match. Tap one to open it:`,
          results,
        },
      ]);
    }
    setBusy(false);
  };

  if (!mounted || !user) return null;

  return createPortal(
    <>
      {/* Launcher */}
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close Stringer assistant" : "Open Stringer, the prompt assistant"}
        className={cn(
          "stringer-launcher fixed bottom-5 right-5 z-[60] flex h-14 w-14 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg outline-none ring-offset-2 ring-offset-background focus-visible:ring-2 focus-visible:ring-primary",
          open && "rotate-0",
        )}
      >
        <span className="stringer-halo absolute inset-0 rounded-full bg-primary/50 blur-md" aria-hidden />
        {open ? (
          <X className="relative h-6 w-6" />
        ) : (
          <Sparkles className="stringer-spark relative h-6 w-6" />
        )}
      </button>

      {/* Panel */}
      {open && (
        <div className="fixed inset-x-3 bottom-24 z-[60] mx-auto flex max-h-[70vh] w-auto max-w-[380px] flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-2xl sm:inset-x-auto sm:right-5 sm:w-[380px]">
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-border bg-gradient-to-r from-primary/10 to-transparent px-4 py-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/15 text-primary">
              <Sparkles className="h-5 w-5" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold leading-tight">Stringer</p>
              <p className="truncate text-xs text-muted-foreground">
                Your prompt-finding assistant
              </p>
            </div>
            <button
              onClick={() => setOpen(false)}
              aria-label="Close"
              className="rounded-md p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-3 py-3">
            {messages.map((m) => (
              <div key={m.id} className={cn("flex", m.role === "user" && "justify-end")}>
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl px-3 py-2 text-sm",
                    m.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground",
                  )}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  {m.results && m.results.length > 0 && (
                    <>
                      <div className="mt-2 space-y-2">
                        {m.results.map((p) => (
                          <Link
                            key={p.id}
                            href={`/prompts/${p.id}`}
                            onClick={() => setOpen(false)}
                            className="block rounded-lg border border-border bg-background p-2.5 transition-colors hover:border-primary/40"
                          >
                            <div className="mb-1 flex items-center gap-1.5">
                              <Badge variant="secondary" className="text-[10px]">
                                {promptTypeLabels[p.prompt_type]}
                              </Badge>
                              {p.category && (
                                <span className="truncate text-[11px] text-muted-foreground">
                                  {p.category.name}
                                </span>
                              )}
                            </div>
                            <p className="line-clamp-1 text-sm font-medium text-foreground">
                              {p.title}
                            </p>
                            {p.description && (
                              <p className="line-clamp-1 text-xs text-muted-foreground">
                                {p.description}
                              </p>
                            )}
                          </Link>
                        ))}
                      </div>
                      <Link
                        href={`/prompts/${m.results[0]!.id}?tab=playground`}
                        onClick={() => setOpen(false)}
                        className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
                      >
                        <Play className="h-3.5 w-3.5" /> Want me to run one? Try the top pick in
                        the Playground →
                      </Link>
                    </>
                  )}
                </div>
              </div>
            ))}
            {busy && (
              <div className="flex">
                <div className="flex items-center gap-2 rounded-2xl bg-muted px-3 py-2 text-sm text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" /> Searching the library…
                </div>
              </div>
            )}

            {/* Quick suggestions before the first user message */}
            {messages.length <= 1 && !busy && (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => respond(s)}
                    className="rounded-full border border-border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              respond(input);
            }}
            className="flex items-center gap-2 border-t border-border p-2.5"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe the prompt you need…"
              className="flex-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <button
              type="submit"
              disabled={busy || !input.trim()}
              aria-label="Send"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </>,
    document.body,
  );
}
