/** Shared API DTOs mirroring the FastAPI schemas. */

export type UserRole =
  | "guest"
  | "viewer"
  | "contributor"
  | "moderator"
  | "administrator";

export interface User {
  id: string;
  email: string;
  username: string | null;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url: string | null;
  bio: string | null;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiErrorBody {
  detail: string;
  code?: string;
}

// --- Prompts ----------------------------------------------------------------
export type PromptType =
  | "ui"
  | "backend"
  | "database"
  | "api"
  | "architecture"
  | "security"
  | "optimization"
  | "testing"
  | "bug_fix"
  | "deployment"
  | "documentation"
  | "code_review"
  | "refactoring"
  | "other";

export type Complexity = "beginner" | "intermediate" | "advanced" | "expert";
export type PromptStatus = "draft" | "published" | "archived";

export type PromptSort =
  | "newest"
  | "oldest"
  | "most_viewed"
  | "most_copied"
  | "most_liked"
  | "title";

export interface PromptAuthor {
  id: string;
  username: string | null;
  full_name: string | null;
  avatar_url: string | null;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  usage_count: number;
}

export interface CategoryRef {
  id: string;
  name: string;
  slug: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  parent_id: string | null;
  position: number;
  created_at: string;
}

export interface CategoryNode extends Category {
  children: CategoryNode[];
}

// --- Project hierarchy ------------------------------------------------------
export interface ComponentRefFull {
  id: string;
  name: string;
  slug: string;
}

export interface ProjectSummary {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  icon: string | null;
  author: { id: string; username: string | null; full_name: string | null };
  created_at: string;
}

export interface ComponentNode {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  position: number;
  prompt_count: number;
}

export interface ModuleNode {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  position: number;
  components: ComponentNode[];
}

export interface ProjectTree extends ProjectSummary {
  modules: ModuleNode[];
}

export interface PromptSummary {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  prompt_type: PromptType;
  complexity: Complexity;
  status: PromptStatus;
  framework: string | null;
  language: string | null;
  ai_model: string | null;
  current_version: number;
  views_count: number;
  copies_count: number;
  likes_count: number;
  forks_count: number;
  author: PromptAuthor;
  category: CategoryRef | null;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export type AssetKind =
  | "screenshot"
  | "image"
  | "video"
  | "live_demo"
  | "generated_html"
  | "generated_code";

export interface PromptAsset {
  id: string;
  kind: AssetKind;
  url: string | null;
  content: string | null;
  language: string | null;
  caption: string | null;
  position: number;
  created_at: string;
}

export interface AssetCreateInput {
  kind: AssetKind;
  url?: string | null;
  content?: string | null;
  language?: string | null;
  caption?: string | null;
  position?: number;
}

export interface PromptDetail extends PromptSummary {
  content: string;
  estimated_tokens: number | null;
  expected_output: string | null;
  actual_output: string | null;
  demo_url: string | null;
  repository_url: string | null;
  documentation_url: string | null;
  forked_from_id: string | null;
  component: ComponentRefFull | null;
  assets: PromptAsset[];
  is_liked: boolean;
  is_bookmarked: boolean;
}

export interface Collection {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  is_public: boolean;
  author: { id: string; username: string | null; full_name: string | null };
  item_count: number;
  created_at: string;
}

export interface CollectionDetail extends Collection {
  items: PromptSummary[];
}

export interface VersionSide {
  version_number: number;
  title: string;
  content: string;
  change_summary: string | null;
}

export interface DiffLine {
  op: "equal" | "insert" | "delete";
  text: string;
}

export interface VersionCompare {
  from_version: VersionSide;
  to_version: VersionSide;
  diff: DiffLine[];
  added: number;
  removed: number;
}

export interface PromptVersion {
  id: string;
  version_number: number;
  title: string;
  content: string;
  change_summary: string | null;
  author_id: string | null;
  created_at: string;
}

export interface PromptCreateInput {
  title: string;
  content: string;
  description?: string | null;
  prompt_type: PromptType;
  complexity: Complexity;
  status: PromptStatus;
  framework?: string | null;
  language?: string | null;
  ai_model?: string | null;
  estimated_tokens?: number | null;
  expected_output?: string | null;
  actual_output?: string | null;
  demo_url?: string | null;
  repository_url?: string | null;
  documentation_url?: string | null;
  category_id?: string | null;
  component_id?: string | null;
  tags?: string[];
}

export type PromptUpdateInput = Partial<Omit<PromptCreateInput, "content">>;

export interface VersionCreateInput {
  content: string;
  title?: string;
  change_summary?: string;
}
