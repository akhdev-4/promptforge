"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";

import { useAuthStore } from "@/stores/auth";

/** Entry gate: send authenticated users to the dashboard, others to login. */
export default function Home() {
  const status = useAuthStore((s) => s.status);
  const router = useRouter();

  React.useEffect(() => {
    if (status === "authenticated") router.replace("/dashboard");
    else if (status === "unauthenticated") router.replace("/login");
  }, [status, router]);

  return (
    <div className="flex h-screen items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );
}
