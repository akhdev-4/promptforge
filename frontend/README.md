# PromptForge — Frontend

Next.js 16 (App Router) · React 19 · TypeScript · Tailwind v4 · TanStack Query ·
next-themes · React Hook Form + Zod · Zustand · Framer Motion (`motion`).

## Quick start

```bash
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev                  # http://localhost:3000
```

The backend must be running (see `../backend/README.md`).

## Architecture

```
src/
├── app/
│   ├── (auth)/            Public auth routes (login, register) — centered layout
│   ├── (app)/             Authenticated routes — sidebar + topbar shell (guarded)
│   ├── layout.tsx         Root: fonts, <Providers>, metadata
│   └── page.tsx           Entry gate → redirects by auth status
├── components/
│   ├── ui/                shadcn-style primitives (button, card, input, badge…)
│   ├── layout/            sidebar, topbar, user-menu, app-shell (auth guard)
│   ├── providers.tsx      React Query + next-themes + auth hydration
│   └── theme-toggle.tsx
├── lib/
│   ├── api.ts             Typed fetch client (auto token + 401 refresh retry)
│   ├── auth-api.ts        Auth endpoint wrappers
│   ├── token-store.ts     Access/refresh persistence (localStorage)
│   ├── config.ts          Public runtime config
│   └── utils.ts           cn(), formatDate()
├── stores/auth.ts         Zustand auth state (login/register/logout/hydrate)
├── config/nav.ts          Sidebar navigation model
└── types/index.ts         API DTOs mirroring backend schemas
```

### Design decisions

- **Route groups** split public (`(auth)`) from guarded (`(app)`) chrome without
  affecting URLs. The `(app)` layout wraps everything in `AppShell`, which
  redirects unauthenticated users to `/login`.
- **Token refresh** is transparent: a 401 triggers a single refresh (concurrent
  requests share it) then retries once.
- **Theming** is class-based via `next-themes`; tokens live in `globals.css`
  (Tailwind v4 `@theme`) and cover light + dark.
- **Next 16 notes**: Turbopack is the default bundler; `params`/`searchParams`
  are async (relevant from M6 onward); `middleware`→`proxy` (we guard on the
  client for now).

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Dev server (Turbopack) |
| `npm run build` | Production build |
| `npm run start` | Serve the production build |
| `npm run lint` | ESLint |
