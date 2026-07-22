import { Logo } from "@/components/brand/logo";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      {/* Ambient gradient backdrop */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 -z-10 opacity-70"
        style={{
          background:
            "radial-gradient(60rem 60rem at 20% -10%, oklch(0.55 0.23 277 / 0.18), transparent 60%), radial-gradient(50rem 50rem at 90% 110%, oklch(0.6 0.18 200 / 0.15), transparent 60%)",
        }}
      />
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center text-center">
          <Logo className="mb-3 h-16 w-auto" />
          <h1 className="text-2xl font-semibold tracking-tight">PromptForge</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Production-tested prompts, reusable by design.
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
