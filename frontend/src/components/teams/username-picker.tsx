"use client";

import { useQuery } from "@tanstack/react-query";
import * as React from "react";

import { Input } from "@/components/ui/input";
import { authApi } from "@/lib/auth-api";
import { cn } from "@/lib/utils";

/**
 * Username input with an @-triggered typeahead.
 *
 * The suggestion list only appears once the value starts with "@"; the text
 * after it filters the (alphabetically ordered) results from the server.
 */
export function UsernamePicker({
  value,
  onChange,
  onSubmit,
  excludeUsernames = [],
  placeholder = "or add @username",
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  /** Usernames to hide (e.g. people already on the team). */
  excludeUsernames?: (string | null)[];
  placeholder?: string;
  className?: string;
}) {
  const [open, setOpen] = React.useState(false);
  const [active, setActive] = React.useState(0);
  const [debounced, setDebounced] = React.useState("");
  const boxRef = React.useRef<HTMLDivElement>(null);

  const isMention = value.startsWith("@");
  const query = isMention ? value.slice(1).trim() : "";

  React.useEffect(() => {
    const t = setTimeout(() => setDebounced(query), 180);
    return () => clearTimeout(t);
  }, [query]);

  const { data, isFetching } = useQuery({
    queryKey: ["user-search", debounced],
    queryFn: () => authApi.searchUsers(debounced),
    enabled: open && isMention,
    staleTime: 30_000,
  });

  const excluded = React.useMemo(
    () => new Set(excludeUsernames.filter(Boolean).map((u) => u!.toLowerCase())),
    [excludeUsernames],
  );
  const options = React.useMemo(
    () => (data ?? []).filter((u) => u.username && !excluded.has(u.username.toLowerCase())),
    [data, excluded],
  );

  // Close when clicking outside.
  React.useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  React.useEffect(() => setActive(0), [debounced]);

  const choose = (username: string) => {
    onChange(`@${username}`);
    setOpen(false);
  };

  const showList = open && isMention;

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (showList && options.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActive((i) => (i + 1) % options.length);
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setActive((i) => (i - 1 + options.length) % options.length);
        return;
      }
      if (e.key === "Enter" && options[active]) {
        e.preventDefault();
        choose(options[active]!.username!);
        return;
      }
    }
    if (e.key === "Enter") onSubmit();
    if (e.key === "Escape") setOpen(false);
  };

  return (
    <div ref={boxRef} className={cn("relative flex-1", className)}>
      <Input
        value={value}
        onChange={(e) => {
          onChange(e.target.value);
          setOpen(true);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        className="h-9"
        autoComplete="off"
      />

      {showList && (
        <div className="absolute left-0 right-0 top-full z-50 mt-1 max-h-56 overflow-y-auto rounded-lg border border-border bg-popover shadow-lg">
          {options.length > 0 ? (
            options.map((u, i) => (
              <button
                key={u.id}
                type="button"
                onClick={() => choose(u.username!)}
                onMouseEnter={() => setActive(i)}
                className={cn(
                  "flex w-full items-center gap-2 px-2.5 py-1.5 text-left text-sm",
                  i === active ? "bg-accent" : "hover:bg-accent/60",
                )}
              >
                <span className="flex h-6 w-6 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-[10px] font-semibold text-primary">
                  {u.avatar_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={u.avatar_url} alt="" className="h-full w-full object-cover" />
                  ) : (
                    (u.username?.[0] ?? "?").toUpperCase()
                  )}
                </span>
                <span className="min-w-0 flex-1 truncate">
                  <span className="font-medium">@{u.username}</span>
                  {u.full_name && (
                    <span className="ml-1.5 text-xs text-muted-foreground">{u.full_name}</span>
                  )}
                </span>
              </button>
            ))
          ) : (
            <p className="px-2.5 py-2 text-xs text-muted-foreground">
              {isFetching ? "Searching…" : "No matching users."}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
