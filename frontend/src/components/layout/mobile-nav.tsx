"use client";

import { Menu, X } from "lucide-react";
import { usePathname } from "next/navigation";
import * as React from "react";
import { createPortal } from "react-dom";

import { Sidebar } from "@/components/layout/sidebar";
import { Button } from "@/components/ui/button";

/**
 * Hamburger + slide-in drawer that reuses the Sidebar. Shown below `lg`.
 *
 * The overlay is portalled to <body> on purpose: the Topbar uses `backdrop-blur`
 * (backdrop-filter), which establishes a containing block for fixed-positioned
 * descendants — so a `fixed inset-0` rendered inside the Topbar would be sized to
 * the 64px header instead of the viewport. Portalling escapes that.
 */
export function MobileNav() {
  const [open, setOpen] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);
  const pathname = usePathname();

  React.useEffect(() => setMounted(true), []);

  // Close on navigation.
  React.useEffect(() => {
    setOpen(false);
  }, [pathname]);

  // Close on Escape + lock body scroll while open.
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("keydown", onKey);
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={() => setOpen(true)}
        aria-label="Open navigation"
      >
        <Menu className="h-5 w-5" />
      </Button>

      {mounted &&
        open &&
        createPortal(
          <div className="fixed inset-0 z-[60] lg:hidden" role="dialog" aria-modal="true">
            <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
            <div className="absolute inset-y-0 left-0 w-72 max-w-[84%] bg-background shadow-2xl">
              <Sidebar className="h-full border-r-0 bg-card backdrop-blur-none" />
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-3.5"
                onClick={() => setOpen(false)}
                aria-label="Close navigation"
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
          </div>,
          document.body,
        )}
    </>
  );
}
