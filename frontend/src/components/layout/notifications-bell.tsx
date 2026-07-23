"use client";

import { Bell } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import {
  useMarkNotificationsRead,
  useNotifications,
  useUnreadCount,
} from "@/hooks/use-community";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export function NotificationsBell() {
  const user = useAuthStore((s) => s.user);
  const [open, setOpen] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);
  const { data: count } = useUnreadCount();
  const { data: items } = useNotifications(open);
  const markRead = useMarkNotificationsRead();
  const unread = count?.unread ?? 0;

  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  if (!user) return null;

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (next && unread > 0) markRead.mutate();
  };

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={toggle}
        className="relative flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unread > 0 && (
          <span className="absolute right-1.5 top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-semibold text-primary-foreground">
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-11 z-50 w-80 overflow-hidden rounded-xl border border-border bg-popover shadow-lg">
          <div className="border-b border-border px-4 py-2.5 text-sm font-semibold">
            Notifications
          </div>
          <div className="max-h-96 overflow-y-auto">
            {items && items.length > 0 ? (
              items.map((n) => {
                const inner = (
                  <div
                    className={cn(
                      "px-4 py-3 text-sm transition-colors hover:bg-accent",
                      !n.is_read && "bg-primary/5",
                    )}
                  >
                    <p className="text-foreground">{n.message}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">
                      {formatDate(n.created_at)}
                    </p>
                  </div>
                );
                return n.link ? (
                  <Link key={n.id} href={n.link} onClick={() => setOpen(false)} className="block">
                    {inner}
                  </Link>
                ) : (
                  <div key={n.id}>{inner}</div>
                );
              })
            ) : (
              <p className="px-4 py-8 text-center text-sm text-muted-foreground">
                You&rsquo;re all caught up.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
