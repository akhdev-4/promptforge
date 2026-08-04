/** Display labels and select options for prompt enums. */

import type { Complexity, PromptStatus, PromptType } from "@/types";

export const promptTypeLabels: Record<PromptType, string> = {
  ui: "UI / Design",
  frontend: "Frontend",
  backend: "Backend",
  full_stack: "Full Stack",
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
  image_generation: "Image Generation",
  photo_editing: "Photo Editing",
  video: "Video",
  writing: "Writing & Copy",
  other: "Other",
};

/**
 * Which types each library lane offers.
 *
 * The lanes serve different audiences, so showing a photo-editing user
 * "Code Review" (or a developer "Image Generation") is just noise. "Other" is
 * in both lists because plenty of existing prompts still use it.
 */
export const DEV_PROMPT_TYPES: PromptType[] = [
  "ui",
  "frontend",
  "backend",
  "full_stack",
  "database",
  "api",
  "architecture",
  "security",
  "optimization",
  "testing",
  "bug_fix",
  "deployment",
  "documentation",
  "code_review",
  "refactoring",
  "other",
];

export const CREATIVE_PROMPT_TYPES: PromptType[] = [
  "image_generation",
  "photo_editing",
  "video",
  "writing",
  "other",
];

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
  ["top_rated", "Top rated"],
  ["title", "Title A–Z"],
];
