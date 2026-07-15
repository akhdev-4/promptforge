"use client";

import { cn } from "@/lib/utils";

export interface TabItem {
  value: string;
  label: string;
  count?: number;
}

export function TabBar({
  tabs,
  value,
  onChange,
}: {
  tabs: TabItem[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="flex gap-1 overflow-x-auto border-b border-border">
      {tabs.map((tab) => {
        const active = tab.value === value;
        return (
          <button
            key={tab.value}
            onClick={() => onChange(tab.value)}
            className={cn(
              "relative whitespace-nowrap px-4 py-2.5 text-sm font-medium transition-colors",
              active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.label}
            {tab.count != null && (
              <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-xs">
                {tab.count}
              </span>
            )}
            {active && (
              <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-primary" />
            )}
          </button>
        );
      })}
    </div>
  );
}
