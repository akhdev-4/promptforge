import { cn } from "@/lib/utils";

/**
 * PromptForge brand mark — the anvil + flame emblem (PNG in /public).
 * Size it by height and let width follow, e.g. `h-9 w-auto`. Transparent
 * background, so it sits cleanly on light and dark surfaces.
 */
export function Logo({ className }: { className?: string }) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src="/promptforge-logo.png"
      alt="PromptForge"
      className={cn("w-auto max-w-full select-none object-contain", className)}
      draggable={false}
    />
  );
}
