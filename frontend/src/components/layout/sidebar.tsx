"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Flame } from "lucide-react";

import { navSections } from "@/config/nav";
import { cn } from "@/lib/utils";

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r border-border bg-card/40 backdrop-blur",
        className,
      )}
    >
      <div className="flex h-16 items-center gap-2 px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
          <Flame className="h-5 w-5" />
        </div>
        <span className="text-lg font-semibold tracking-tight">PromptForge</span>
      </div>

      <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4">
        {navSections.map((section) => (
          <div key={section.title}>
            <p className="px-3 pb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              {section.title}
            </p>
            <ul className="space-y-1">
              {section.items.map((item) => {
                const active =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                const Icon = item.icon;
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      )}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      <span className="flex-1">{item.label}</span>
                      {item.soon && (
                        <span className="rounded-md bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                          soon
                        </span>
                      )}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      <div className="border-t border-border p-4 text-xs text-muted-foreground">
        v0.1.0 · Milestone 3
      </div>
    </aside>
  );
}
