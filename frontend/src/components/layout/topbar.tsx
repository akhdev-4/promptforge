"use client";

import { MobileNav } from "@/components/layout/mobile-nav";
import { NotificationsBell } from "@/components/layout/notifications-bell";
import { ThemeToggle } from "@/components/theme-toggle";
import { UserMenu } from "@/components/layout/user-menu";

export function Topbar() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur sm:px-6">
      <MobileNav />
      <div className="ml-auto flex items-center gap-1">
        <NotificationsBell />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
