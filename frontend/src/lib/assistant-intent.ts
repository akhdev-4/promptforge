/** Parse a natural-language assistant query into a topic + optional sort. */

import type { PromptSort, PromptSummary } from "@/types";

export interface Intent {
  /** Meaningful search terms with filler/sort words removed. */
  topic: string;
  sort?: PromptSort;
  /** Human label for the detected sort, e.g. "top-rated". */
  sortLabel?: string;
}

// Order matters — the first match wins.
const SORT_PATTERNS: [RegExp, PromptSort, string][] = [
  [/top[\s-]?rated|highest[\s-]?rated|best[\s-]?rated|highly[\s-]?rated|\bbest\b/, "top_rated", "top-rated"],
  [/most[\s-]?copied|most[\s-]?used/, "most_copied", "most-copied"],
  [/most[\s-]?popular|\bpopular\b|trending/, "most_copied", "most-popular"],
  [/most[\s-]?liked|most[\s-]?loved/, "most_liked", "most-liked"],
  [/most[\s-]?viewed|most[\s-]?seen/, "most_viewed", "most-viewed"],
  [/newest|latest|recent|\bnew\b/, "newest", "newest"],
  [/oldest/, "oldest", "oldest"],
];

// Words stripped when extracting the core topic (filler + ranking words).
const STOP = new Set([
  "show", "me", "the", "a", "an", "for", "prompt", "prompts", "find", "get",
  "give", "please", "some", "any", "of", "to", "with", "that", "top", "rated",
  "best", "highest", "highly", "most", "copied", "popular", "trending",
  "newest", "latest", "recent", "liked", "loved", "viewed", "seen", "oldest",
  "used", "i", "want", "need", "looking", "search", "would", "like", "is",
  "are", "and", "in", "on", "about",
]);

export function parseIntent(text: string): Intent {
  const lower = text.toLowerCase();
  let sort: PromptSort | undefined;
  let sortLabel: string | undefined;
  for (const [re, s, label] of SORT_PATTERNS) {
    if (re.test(lower)) {
      sort = s;
      sortLabel = label;
      break;
    }
  }
  const topic = lower
    .replace(/[^a-z0-9\s]/g, " ")
    .split(/\s+/)
    .filter((w) => w && !STOP.has(w))
    .join(" ")
    .trim();
  return { topic, sort, sortLabel };
}

type Comparator = (a: PromptSummary, b: PromptSummary) => number;
const time = (s: string) => new Date(s).getTime();

const COMPARATORS: Record<PromptSort, Comparator> = {
  top_rated: (a, b) => b.rating_avg - a.rating_avg || b.rating_count - a.rating_count,
  most_copied: (a, b) => b.copies_count - a.copies_count,
  most_liked: (a, b) => b.likes_count - a.likes_count,
  most_viewed: (a, b) => b.views_count - a.views_count,
  newest: (a, b) => time(b.created_at) - time(a.created_at),
  oldest: (a, b) => time(a.created_at) - time(b.created_at),
  title: (a, b) => a.title.localeCompare(b.title),
};

/** Re-rank an already-relevant set by the requested sort. */
export function sortPrompts(list: PromptSummary[], sort: PromptSort): PromptSummary[] {
  const cmp = COMPARATORS[sort];
  return cmp ? [...list].sort(cmp) : list;
}
