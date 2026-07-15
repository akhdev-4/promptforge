"use client";

import { LogOut, User as UserIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

function initials(name: string | null, email: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/);
    return (parts[0]![0] + (parts[1]?.[0] ?? "")).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

export function UserMenu() {
  const { user, logout } = useAuthStore();
  const router = useRouter();
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
          {initials(user.full_name, user.email)}
        </span>
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-border bg-popover shadow-lg">
          <div className="border-b border-border px-4 py-3">
            <p className="truncate text-sm font-medium">
              {user.full_name ?? user.username ?? "User"}
            </p>
            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            <span className="mt-1 inline-block rounded-md bg-primary/10 px-1.5 py-0.5 text-[10px] font-medium uppercase text-primary">
              {user.role}
            </span>
          </div>
          <div className="p-1">
            <button
              className={cn(
                "flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm",
                "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
              disabled
            >
              <UserIcon className="h-4 w-4" /> Profile
              <span className="ml-auto text-[10px]">soon</span>
            </button>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
            >
              <LogOut className="h-4 w-4" /> Log out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
