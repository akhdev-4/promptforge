"use client";

import { AlertCircle, CheckCircle2, Info, X } from "lucide-react";
import * as React from "react";
import { createPortal } from "react-dom";

import { cn } from "@/lib/utils";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastApi {
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}

const noop = () => {};
const ToastContext = React.createContext<ToastApi>({
  success: noop,
  error: noop,
  info: noop,
});

const STYLES: Record<ToastType, string> = {
  success: "border-green-500/30 bg-green-500/10 text-green-700 dark:text-green-300",
  error: "border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300",
  info: "border-primary/30 bg-primary/10 text-foreground",
};
const ICONS: Record<ToastType, typeof Info> = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const dismiss = React.useCallback((id: number) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const push = React.useCallback(
    (message: string, type: ToastType) => {
      const id = Date.now() + Math.random();
      setToasts((t) => [...t, { id, message, type }]);
      setTimeout(() => dismiss(id), 3500);
    },
    [dismiss],
  );

  const api = React.useMemo<ToastApi>(
    () => ({
      success: (m) => push(m, "success"),
      error: (m) => push(m, "error"),
      info: (m) => push(m, "info"),
    }),
    [push],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      {mounted &&
        createPortal(
          <div className="pointer-events-none fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
            {toasts.map((toast) => {
              const Icon = ICONS[toast.type];
              return (
                <div
                  key={toast.id}
                  className={cn(
                    "pf-toast pointer-events-auto flex w-72 items-start gap-2 rounded-xl border px-4 py-3 shadow-lg backdrop-blur",
                    STYLES[toast.type],
                  )}
                  role="status"
                >
                  <Icon className="mt-0.5 h-4 w-4 shrink-0" />
                  <p className="flex-1 text-sm">{toast.message}</p>
                  <button
                    onClick={() => dismiss(toast.id)}
                    className="shrink-0 opacity-60 hover:opacity-100"
                    aria-label="Dismiss"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>,
          document.body,
        )}
    </ToastContext.Provider>
  );
}

export function useToast(): ToastApi {
  return React.useContext(ToastContext);
}
