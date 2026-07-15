"use client";

import { Search } from "lucide-react";

import { ThemeToggle } from "@/components/theme-toggle";
import { UserMenu } from "@/components/layout/user-menu";

export function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/80 px-6 backdrop-blur">
      <div className="relative hidden max-w-md flex-1 md:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <input
          disabled
          placeholder="Search prompts, components, collections…"
          className="h-10 w-full rounded-lg border border-input bg-muted/40 pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed"
        />
        <kbd className="absolute right-3 top-1/2 -translate-y-1/2 rounded border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground">
          ⌘K
        </kbd>
      </div>
      <div className="flex flex-1 items-center justify-end gap-1 md:flex-none">
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
