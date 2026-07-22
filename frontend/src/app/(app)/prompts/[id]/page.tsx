"use client";

import {
  ArrowLeft,
  Bookmark,
  Calendar,
  Copy,
  Eye,
  GitFork,
  Heart,
  Layers,
  Pencil,
  Play,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import * as React from "react";

import { AddToCollection } from "@/components/prompts/add-to-collection";
import { AssetManager } from "@/components/prompts/asset-manager";
import { CodeView } from "@/components/prompts/code-view";
import { CopyButton } from "@/components/prompts/copy-button";
import { LivePreview } from "@/components/prompts/live-preview";
import { MarkdownView } from "@/components/prompts/markdown-view";
import { Playground } from "@/components/prompts/playground";
import { PreviewGallery } from "@/components/prompts/preview-gallery";
import { VersionDiff } from "@/components/prompts/version-diff";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { TabBar, type TabItem } from "@/components/ui/tabs";
import { PromptCard } from "@/components/prompts/prompt-card";
import { StarRating } from "@/components/prompts/star-rating";
import { useRatePrompt, useToggleBookmark, useToggleLike } from "@/hooks/use-collections";
import {
  useCompareVersions,
  useDeletePrompt,
  useForkPrompt,
  usePrompt,
  usePromptVersions,
  useRelatedPrompts,
} from "@/hooks/use-prompts";
import { cn } from "@/lib/utils";
import { complexityLabels, promptTypeLabels, statusLabels } from "@/lib/prompt-meta";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

function authorInitials(fullName: string | null, username: string | null): string {
  const base = (fullName?.trim() || username?.trim() || "?").split(/\s+/);
  return (base[0]![0]! + (base[1]?.[0] ?? "")).toUpperCase();
}

function MetaRow({ label, value }: { label: string; value: React.ReactNode }) {
  if (!value) return null;
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium">{value}</span>
    </div>
  );
}

export default function PromptDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const user = useAuthStore((s) => s.user);

  const { data: prompt, isLoading, isError } = usePrompt(id);
  const { data: versions } = usePromptVersions(id);
  const del = useDeletePrompt();
  const fork = useForkPrompt();
  const like = useToggleLike(id);
  const bookmark = useToggleBookmark(id);
  const rate = useRatePrompt(id);
  const { data: related } = useRelatedPrompts(id);
  const [tab, setTab] = React.useState("overview");
  const [pgSeen, setPgSeen] = React.useState(true); // assume seen until we read storage (avoids flash)
  const panelRef = React.useRef<HTMLDivElement>(null);
  const deepLinked = React.useRef(false);

  React.useEffect(() => {
    setPgSeen(localStorage.getItem("pf_playground_seen") === "1");
  }, []);

  const markPlaygroundSeen = React.useCallback(() => {
    localStorage.setItem("pf_playground_seen", "1");
    setPgSeen(true);
  }, []);

  const goToPlayground = React.useCallback(() => {
    setTab("playground");
    markPlaygroundSeen();
    requestAnimationFrame(() =>
      panelRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
    );
  }, [markPlaygroundSeen]);

  const handleTabChange = React.useCallback(
    (value: string) => {
      setTab(value);
      if (value === "playground") markPlaygroundSeen();
    },
    [markPlaygroundSeen],
  );

  // Deep link: /prompts/{id}?tab=playground opens the Playground directly.
  React.useEffect(() => {
    if (deepLinked.current || !user) return;
    if (new URLSearchParams(window.location.search).get("tab") === "playground") {
      deepLinked.current = true;
      goToPlayground();
    }
  }, [user, goToPlayground]);

  // Version compare state.
  const [fromV, setFromV] = React.useState<number | null>(null);
  const [toV, setToV] = React.useState<number | null>(null);
  const compare = useCompareVersions(id, fromV, toV);

  React.useEffect(() => {
    if (versions && versions.length >= 2 && fromV == null && toV == null) {
      setFromV(versions[versions.length - 1]!.version_number); // oldest
      setToV(versions[0]!.version_number); // newest
    }
  }, [versions, fromV, toV]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  if (isError || !prompt) {
    return (
      <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
        Prompt not found.
      </div>
    );
  }

  const isOwner = user?.id === prompt.author.id;
  const canModerate = user?.role === "moderator" || user?.role === "administrator";
  const canEdit = isOwner || canModerate;

  // Image generation only makes sense for image/creative prompts — not code.
  const isImagePrompt =
    /image|photo|portrait|avatar|art|illustration|sticker|logo|social|creative|editing/i.test(
      `${prompt.category?.name ?? ""} ${prompt.title}`,
    );

  const shots = prompt.assets.filter((a) => a.kind === "screenshot" || a.kind === "image");
  const lives = prompt.assets.filter((a) => a.kind === "generated_html" || a.kind === "live_demo");
  const codes = prompt.assets.filter((a) => a.kind === "generated_code");

  const tabs: TabItem[] = [{ value: "overview", label: "Overview" }];
  if (user) tabs.push({ value: "playground", label: "Playground", dot: !pgSeen });
  tabs.push(
    { value: "preview", label: "Preview", count: shots.length + lives.length || undefined },
    { value: "code", label: "Code", count: codes.length || undefined },
    { value: "versions", label: "Versions", count: prompt.current_version },
  );
  if (canEdit) tabs.push({ value: "assets", label: "Manage previews" });

  const onDelete = async () => {
    if (!window.confirm("Delete this prompt and all its versions?")) return;
    await del.mutateAsync(prompt.id);
    router.push("/prompts");
  };
  const onFork = async () => {
    const forked = await fork.mutateAsync(prompt.id);
    router.push(`/prompts/${forked.id}`);
  };

  return (
    <div className="space-y-6">
      <Link
        href="/prompts"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> Back to library
      </Link>

      {/* Header */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="default">{promptTypeLabels[prompt.prompt_type]}</Badge>
            <Badge variant="secondary">{complexityLabels[prompt.complexity]}</Badge>
            {prompt.status !== "published" && (
              <Badge variant="warning">{statusLabels[prompt.status]}</Badge>
            )}
            {prompt.forked_from_id && (
              <Badge variant="outline">
                <GitFork className="mr-1 h-3 w-3" /> Fork
              </Badge>
            )}
          </div>
          <h1 className="text-2xl font-semibold tracking-tight">{prompt.title}</h1>
          {prompt.description && (
            <p className="max-w-2xl text-sm text-muted-foreground">{prompt.description}</p>
          )}
          {prompt.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {prompt.tags.map((t) => (
                <Badge key={t.id} variant="secondary">
                  #{t.slug}
                </Badge>
              ))}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-x-5 gap-y-3 text-xs text-muted-foreground">
            {/* Who added this prompt */}
            <span className="flex items-center gap-2">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-xs font-semibold text-primary">
                {prompt.author.avatar_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={prompt.author.avatar_url}
                    alt=""
                    className="h-full w-full object-cover"
                  />
                ) : (
                  authorInitials(prompt.author.full_name, prompt.author.username)
                )}
              </span>
              <span className="flex flex-col leading-tight">
                <span className="flex items-center gap-1.5 text-sm font-medium text-foreground">
                  {prompt.author.full_name ?? prompt.author.username ?? "Unknown user"}
                  {isOwner && (
                    <Badge variant="secondary" className="px-1.5 py-0 text-[10px]">
                      You
                    </Badge>
                  )}
                </span>
                {prompt.author.username && <span>@{prompt.author.username}</span>}
              </span>
            </span>

            <span className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" /> Added {formatDate(prompt.created_at)}
            </span>
            <span className="flex items-center gap-1">
              <Eye className="h-3.5 w-3.5" /> {prompt.views_count}
            </span>
            <span className="flex items-center gap-1">
              <Copy className="h-3.5 w-3.5" /> {prompt.copies_count}
            </span>
            <span className="flex items-center gap-1">
              <GitFork className="h-3.5 w-3.5" /> {prompt.forks_count}
            </span>
          </div>

          {/* Ownership note for non-owners */}
          {user && !canEdit && (
            <p className="text-xs text-muted-foreground">
              Only{" "}
              <span className="font-medium text-foreground">
                {prompt.author.full_name ?? prompt.author.username ?? "the author"}
              </span>{" "}
              can edit this prompt. You can copy, fork, or save it.
            </p>
          )}

          {/* Star ratings */}
          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 rounded-xl border border-border bg-card/60 px-4 py-3">
            <div className="flex items-center gap-2">
              <StarRating value={prompt.rating_avg} readOnly size="md" />
              <span className="text-sm">
                <span className="font-semibold">{prompt.rating_avg.toFixed(1)}</span>
                <span className="text-muted-foreground">
                  {" · "}
                  {prompt.rating_count} rating{prompt.rating_count === 1 ? "" : "s"}
                </span>
              </span>
            </div>
            {user && (
              <div className="flex items-center gap-2 sm:ml-auto">
                <span className="text-xs text-muted-foreground">
                  {prompt.my_rating ? "Your rating" : "Rate it"}
                </span>
                <StarRating
                  value={prompt.my_rating ?? 0}
                  onRate={(s) => rate.mutate(s)}
                  size="md"
                />
                {prompt.my_rating != null && (
                  <button
                    onClick={() => rate.mutate(null)}
                    disabled={rate.isPending}
                    className="text-xs text-muted-foreground underline-offset-2 hover:text-foreground hover:underline"
                  >
                    Clear
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <CopyButton promptId={prompt.id} content={prompt.content} />
          {user && (
            <Button onClick={goToPlayground}>
              <Play className="h-4 w-4" /> Run prompt
            </Button>
          )}
          {user && (
            <>
              <Button
                variant="outline"
                onClick={() => like.mutate()}
                disabled={like.isPending}
                aria-pressed={prompt.is_liked}
                aria-label={prompt.is_liked ? "Unlike" : "Like"}
                title={prompt.is_liked ? "Unlike" : "Like this prompt"}
                className={cn(
                  prompt.is_liked &&
                    "border-destructive/40 bg-destructive/10 text-destructive hover:bg-destructive/15",
                )}
              >
                <Heart
                  className={cn(
                    "h-4 w-4",
                    prompt.is_liked && "fill-destructive text-destructive",
                  )}
                />
                {prompt.likes_count}
              </Button>
              <Button
                variant="outline"
                onClick={() => bookmark.mutate()}
                disabled={bookmark.isPending}
                aria-pressed={prompt.is_bookmarked}
                aria-label={
                  prompt.is_bookmarked ? "Remove from Favorites" : "Save to Favorites"
                }
                title={
                  prompt.is_bookmarked
                    ? "Remove from your Favorites"
                    : "Save to your Favorites"
                }
                className={cn(
                  prompt.is_bookmarked &&
                    "border-primary bg-primary/10 text-primary hover:bg-primary/15",
                )}
              >
                <Bookmark
                  className={cn(
                    "h-4 w-4",
                    prompt.is_bookmarked && "fill-primary text-primary",
                  )}
                />
                {prompt.is_bookmarked ? "In Favorites" : "Save to Favorites"}
              </Button>
              <AddToCollection promptId={prompt.id} />
            </>
          )}
          {user && (
            <Button variant="outline" onClick={onFork} disabled={fork.isPending}>
              <GitFork className="h-4 w-4" /> Fork
            </Button>
          )}
          {canEdit && (
            <Button variant="outline" asChild>
              <Link href={`/prompts/${prompt.id}/edit`}>
                <Pencil className="h-4 w-4" /> Edit
              </Link>
            </Button>
          )}
          {(isOwner || user?.role === "administrator") && (
            <Button variant="destructive" onClick={onDelete} disabled={del.isPending}>
              <Trash2 className="h-4 w-4" /> Delete
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main tabbed panel */}
        <div ref={panelRef} className="space-y-4 lg:col-span-2">
          <TabBar tabs={tabs} value={tab} onChange={handleTabChange} />

          {tab === "overview" && (
            <div className="space-y-6">
              {user && (
                <button
                  onClick={goToPlayground}
                  className="flex w-full items-center gap-3 rounded-xl border border-primary/30 bg-gradient-to-r from-primary/10 to-transparent p-3 text-left transition-colors hover:from-primary/15"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <Play className="h-4 w-4" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-medium">
                      See what this prompt actually produces
                    </span>
                    <span className="block text-xs text-muted-foreground">
                      Run it live in the Playground — real output, no copy-paste.
                    </span>
                  </span>
                  <span className="hidden shrink-0 text-sm font-medium text-primary sm:block">
                    Open Playground →
                  </span>
                </button>
              )}

              <Card>
                <CardHeader className="flex-row items-center justify-between">
                  <CardTitle>Prompt</CardTitle>
                  <CopyButton
                    promptId={prompt.id}
                    content={prompt.content}
                    variant="ghost"
                    size="sm"
                    label="Copy"
                  />
                </CardHeader>
                <CardContent>
                  <MarkdownView content={prompt.content} />
                </CardContent>
              </Card>

              {/* Visual expected output — animated preview of the produced UI. */}
              {lives.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Expected result</CardTitle>
                    <CardDescription>
                      A live, animated preview of what this prompt produces.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <LivePreview assets={prompt.assets} />
                  </CardContent>
                </Card>
              )}

              {prompt.expected_output && (
                <Card>
                  <CardHeader>
                    <CardTitle>{lives.length > 0 ? "What you get" : "Expected output"}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <MarkdownView content={prompt.expected_output} />
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {tab === "playground" && (
            <Playground
              promptId={prompt.id}
              content={prompt.content}
              allowImage={isImagePrompt}
              defaultMode={isImagePrompt ? "image" : "text"}
            />
          )}

          {tab === "preview" && (
            <div className="space-y-6">
              <PreviewGallery assets={prompt.assets} />
              <LivePreview assets={prompt.assets} />
            </div>
          )}

          {tab === "code" && <CodeView assets={prompt.assets} promptId={prompt.id} />}

          {tab === "versions" && (
            <div className="space-y-6">
              {versions && versions.length >= 2 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Compare versions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Select
                        value={fromV ?? ""}
                        onChange={(e) => setFromV(Number(e.target.value))}
                        className="w-28"
                      >
                        {versions.map((v) => (
                          <option key={v.id} value={v.version_number}>
                            v{v.version_number}
                          </option>
                        ))}
                      </Select>
                      <span className="text-muted-foreground">→</span>
                      <Select
                        value={toV ?? ""}
                        onChange={(e) => setToV(Number(e.target.value))}
                        className="w-28"
                      >
                        {versions.map((v) => (
                          <option key={v.id} value={v.version_number}>
                            v{v.version_number}
                          </option>
                        ))}
                      </Select>
                    </div>
                    {compare.data ? (
                      <VersionDiff data={compare.data} />
                    ) : fromV === toV ? (
                      <p className="text-sm text-muted-foreground">
                        Pick two different versions to see the diff.
                      </p>
                    ) : (
                      <Skeleton className="h-32 w-full" />
                    )}
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Layers className="h-4 w-4 text-primary" /> History
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="relative space-y-4 border-l border-border pl-4">
                    {versions?.map((v) => (
                      <li key={v.id} className="relative">
                        <span className="absolute -left-[1.32rem] top-1 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">v{v.version_number}</span>
                          <span className="text-xs text-muted-foreground">
                            {formatDate(v.created_at)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {v.change_summary ?? "No summary"}
                        </p>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>
            </div>
          )}

          {tab === "assets" && canEdit && <AssetManager promptId={prompt.id} />}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Metadata</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-border">
              <MetaRow label="Category" value={prompt.category?.name} />
              <MetaRow
                label="Component"
                value={
                  prompt.component ? (
                    <Link
                      href={`/prompts?component_id=${prompt.component.id}`}
                      className="text-primary hover:underline"
                    >
                      {prompt.component.name}
                    </Link>
                  ) : null
                }
              />
              <MetaRow label="Framework" value={prompt.framework} />
              <MetaRow label="Language" value={prompt.language} />
              <MetaRow label="AI model" value={prompt.ai_model} />
              <MetaRow
                label="Est. tokens"
                value={prompt.estimated_tokens?.toLocaleString()}
              />
              <MetaRow label="Version" value={`v${prompt.current_version}`} />
              <MetaRow label="Created" value={formatDate(prompt.created_at)} />
              <MetaRow label="Updated" value={formatDate(prompt.updated_at)} />
              {prompt.demo_url && (
                <MetaRow
                  label="Demo"
                  value={
                    <a
                      href={prompt.demo_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary hover:underline"
                    >
                      Open
                    </a>
                  }
                />
              )}
              {prompt.repository_url && (
                <MetaRow
                  label="Repo"
                  value={
                    <a
                      href={prompt.repository_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary hover:underline"
                    >
                      Open
                    </a>
                  }
                />
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Recommendations */}
      {related && related.length > 0 && (
        <div className="space-y-3 border-t border-border pt-6">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Related prompts</h2>
            <Badge variant="secondary">recommended</Badge>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {related.map((p) => (
              <PromptCard key={p.id} prompt={p} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
