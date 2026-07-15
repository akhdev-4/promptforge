"use client";

import * as React from "react";

import { AreaChart } from "@/components/charts/area-chart";
import { BarChart } from "@/components/charts/bar-chart";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useByType, useGrowth, useOverview } from "@/hooks/use-analytics";

export default function AnalyticsPage() {
  const [days, setDays] = React.useState(30);
  const { data: overview } = useOverview();
  const { data: growth } = useGrowth(days);
  const { data: byType } = useByType();

  const tiles = overview
    ? [
        ["Prompts", overview.total_prompts],
        ["Views", overview.total_views],
        ["Copies", overview.total_copies],
        ["Likes", overview.total_likes],
        ["Categories", overview.total_categories],
        ["Tags", overview.total_tags],
      ]
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Usage and growth across the prompt knowledge base.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {tiles.length > 0
          ? tiles.map(([label, value]) => (
              <Card key={label as string}>
                <CardContent className="p-4">
                  <p className="text-2xl font-semibold tracking-tight">
                    {(value as number).toLocaleString()}
                  </p>
                  <p className="text-xs text-muted-foreground">{label}</p>
                </CardContent>
              </Card>
            ))
          : Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-20 w-full rounded-xl" />
            ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <div>
              <CardTitle>Prompt growth</CardTitle>
              <CardDescription>New prompts over time</CardDescription>
            </div>
            <Select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-28"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
            </Select>
          </CardHeader>
          <CardContent>
            {growth ? <AreaChart data={growth} /> : <Skeleton className="h-44 w-full" />}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>By type</CardTitle>
            <CardDescription>Prompt distribution</CardDescription>
          </CardHeader>
          <CardContent>
            {byType ? <BarChart data={byType} /> : <Skeleton className="h-44 w-full" />}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
