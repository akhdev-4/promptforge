/** Display labels and select options for prompt enums. */

import type { Complexity, PromptStatus, PromptType } from "@/types";

export const promptTypeLabels: Record<PromptType, string> = {
  ui: "UI",
  backend: "Backend",
  database: "Database",
  api: "API",
  architecture: "Architecture",
  security: "Security",
  optimization: "Optimization",
  testing: "Testing",
  bug_fix: "Bug Fix",
  deployment: "Deployment",
  documentation: "Documentation",
  code_review: "Code Review",
  refactoring: "Refactoring",
  other: "Other",
};

export const complexityLabels: Record<Complexity, string> = {
  beginner: "Beginner",
  intermediate: "Intermediate",
  advanced: "Advanced",
  expert: "Expert",
};

export const statusLabels: Record<PromptStatus, string> = {
  draft: "Draft",
  published: "Published",
  archived: "Archived",
};

export const promptTypeOptions = Object.entries(promptTypeLabels) as [
  PromptType,
  string,
][];
export const complexityOptions = Object.entries(complexityLabels) as [
  Complexity,
  string,
][];
export const statusOptions = Object.entries(statusLabels) as [PromptStatus, string][];

export const sortOptions: [string, string][] = [
  ["newest", "Newest"],
  ["oldest", "Oldest"],
  ["most_viewed", "Most viewed"],
  ["most_copied", "Most copied"],
  ["most_liked", "Most liked"],
  ["title", "Title A–Z"],
];
