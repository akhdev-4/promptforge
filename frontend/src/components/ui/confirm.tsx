"use client";

import * as React from "react";
import { createPortal } from "react-dom";

import { Button } from "@/components/ui/button";

export interface ConfirmOptions {
  title?: string;
  description?: React.ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  destructive?: boolean;
  /**
   * Optional third choice — an alternative to the main action rather than a
   * cancel. Picking it runs `onAlt` and resolves false, so callers still just
   * check the boolean to decide whether to proceed.
   */
  altLabel?: string;
  onAlt?: () => void;
}

type ConfirmFn = (options: ConfirmOptions) => Promise<boolean>;

const ConfirmContext = React.createContext<ConfirmFn>(async () => false);

interface Pending {
  options: ConfirmOptions;
  resolve: (ok: boolean) => void;
}

export function ConfirmProvider({ children }: { children: React.ReactNode }) {
  const [pending, setPending] = React.useState<Pending | null>(null);
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const confirm = React.useCallback<ConfirmFn>((options) => {
    return new Promise<boolean>((resolve) => setPending({ options, resolve }));
  }, []);

  const settle = React.useCallback(
    (ok: boolean) => {
      pending?.resolve(ok);
      setPending(null);
    },
    [pending],
  );

  React.useEffect(() => {
    if (!pending) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") settle(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [pending, settle]);

  return (
    <ConfirmContext.Provider value={confirm}>
      {children}
      {mounted &&
        pending &&
        createPortal(
          <div className="fixed inset-0 z-[90] flex items-center justify-center p-4">
            <div
              className="absolute inset-0 bg-black/50 backdrop-blur-sm"
              onClick={() => settle(false)}
            />
            <div
              role="alertdialog"
              aria-modal="true"
              className="pf-onb-pop relative w-full max-w-sm rounded-2xl border border-border bg-card p-6 shadow-2xl"
            >
              <h2 className="text-lg font-semibold tracking-tight">
                {pending.options.title ?? "Are you sure?"}
              </h2>
              {pending.options.description && (
                <div className="mt-2 text-sm text-muted-foreground">
                  {pending.options.description}
                </div>
              )}
              <div className="mt-6 flex flex-wrap justify-end gap-2">
                <Button variant="ghost" size="sm" onClick={() => settle(false)}>
                  {pending.options.cancelLabel ?? "Cancel"}
                </Button>
                {pending.options.altLabel && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      pending.options.onAlt?.();
                      settle(false);
                    }}
                  >
                    {pending.options.altLabel}
                  </Button>
                )}
                <Button
                  variant={pending.options.destructive ? "destructive" : "default"}
                  size="sm"
                  onClick={() => settle(true)}
                >
                  {pending.options.confirmLabel ?? "Confirm"}
                </Button>
              </div>
            </div>
          </div>,
          document.body,
        )}
    </ConfirmContext.Provider>
  );
}

/** Returns an async `confirm(options)` that resolves true/false. */
export function useConfirm(): ConfirmFn {
  return React.useContext(ConfirmContext);
}
