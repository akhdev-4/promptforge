/** Client-side runtime configuration (public env vars only). */
export const config = {
  apiBaseUrl:
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000",
  apiV1: "/api/v1",
  appName: "PromptForge",
} as const;

export const apiUrl = (path: string) =>
  `${config.apiBaseUrl}${config.apiV1}${path.startsWith("/") ? path : `/${path}`}`;
