"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import * as React from "react";

import { Button } from "@/components/ui/button";

const order = ["light", "dark", "system"] as const;
const icons = { light: Sun, dark: Moon, system: Monitor };

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => setMounted(true), []);

  const current = (mounted ? theme : "system") as keyof typeof icons;
  const Icon = icons[current] ?? Monitor;

  const cycle = () => {
    const idx = order.indexOf(current as (typeof order)[number]);
    setTheme(order[(idx + 1) % order.length]);
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={cycle}
      aria-label={`Theme: ${current}. Click to change.`}
      title={`Theme: ${current}`}
    >
      <Icon className="h-[1.15rem] w-[1.15rem]" />
    </Button>
  );
}
