"use client";

import {
  BookMarked,
  Copy,
  Eye,
  FolderKanban,
  Heart,
  Library,
  Sparkles,
  TrendingUp,
  Trophy,
} from "lucide-react";
import Link from "next/link";

import { AreaChart } from "@/components/charts/area-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useByType,
  useContributors,
  useGrowth,
  useOverview,
  useTrending,
} from "@/hooks/use-analytics";
import { useAuthStore } from "@/stores/auth";

function initials(name: string | null, username: string | null): string {
  const s = name ?? username ?? "?";
  return s.slice(0, 2).toUpperCase();
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const greetingName = (user?.full_name ?? user?.username ?? "there").split(" ")[0];

  const { data: overview, isLoading: ovLoading } = useOverview();
  const { data: growth } = useGrowth(30);
  const { data: byType } = useByType();
  const { data: trending } = useTrending(5);
  const { data: contributors } = useContributors(5);

  const stats = [
    { label: "Total Prompts", value: overview?.total_prompts, icon: Library },
    { label: "Projects", value: overview?.total_projects, icon: FolderKanban },
    { label: "Collections", value: overview?.total_collections, icon: BookMarked },
    { label: "Total Copies", value: overview?.total_copies, icon: Copy },
  ];

  const engagement = [
    { label: "Views", value: overview?.total_views, icon: Eye },
    { label: "Copies", value: overview?.total_copies, icon: Copy },
    { label: "Likes", value: overview?.total_likes, icon: Heart },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Welcome back, {greetingName} 👋
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Your organization&apos;s prompt knowledge base at a glance.
          </p>
        </div>
        <Button asChild>
          <Link href="/prompts/new">
            <Sparkles className="h-4 w-4" />
            New Prompt
          </Link>
        </Button>
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.label} className="transition-shadow hover:shadow-md">
              <CardContent className="p-6">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </span>
                {ovLoading ? (
                  <Skeleton className="mt-4 h-9 w-16" />
                ) : (
                  <p className="mt-4 text-3xl font-semibold tracking-tight">
                    {(s.value ?? 0).toLocaleString()}
                  </p>
                )}
                <p className="text-sm text-muted-foreground">{s.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Prompt growth</CardTitle>
            <CardDescription>New prompts added over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>{growth ? <AreaChart data={growth} /> : <Skeleton className="h-44 w-full" />}</CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>By type</CardTitle>
            <CardDescription>Distribution across prompt types</CardDescription>
          </CardHeader>
          <CardContent>{byType ? <BarChart data={byType} /> : <Skeleton className="h-44 w-full" />}</CardContent>
        </Card>
      </div>

      {/* Engagement + trending + contributors */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Engagement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {engagement.map((e) => {
              const Icon = e.icon;
              return (
                <div key={e.label} className="flex items-center justify-between">
                  <span className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Icon className="h-4 w-4" /> {e.label}
                  </span>
                  <span className="font-semibold">{(e.value ?? 0).toLocaleString()}</span>
                </div>
              );
            })}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-primary" /> Trending
            </CardTitle>
            <CardDescription>Most-copied prompts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {trending && trending.length > 0 ? (
              trending.map((p) => (
                <Link
                  key={p.id}
                  href={`/prompts/${p.id}`}
                  className="flex items-center justify-between rounded-lg px-2 py-1.5 text-sm hover:bg-accent"
                >
                  <span className="truncate">{p.title}</span>
                  <Badge variant="secondary">
                    <Copy className="mr-1 h-3 w-3" />
                    {p.copies_count}
                  </Badge>
                </Link>
              ))
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">No prompts yet.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-4 w-4 text-primary" /> Top contributors
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {contributors && contributors.length > 0 ? (
              contributors.map((c) => (
                <div key={c.id} className="flex items-center justify-between">
                  <span className="flex items-center gap-2 text-sm">
                    <span className="flex h-7 w-7 items-center justify-center rounded-full bg-primary/15 text-xs font-semibold text-primary">
                      {initials(c.full_name, c.username)}
                    </span>
                    {c.full_name ?? c.username ?? "unknown"}
                  </span>
                  <Badge variant="secondary">{c.prompt_count}</Badge>
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-sm text-muted-foreground">
                No contributors yet.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
