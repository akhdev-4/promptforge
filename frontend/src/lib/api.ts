/**
 * Typed fetch client for the PromptForge API.
 *
 * - Attaches the access token automatically.
 * - Transparently refreshes once on a 401, then retries the request.
 * - Normalises errors into `ApiError` so UI code can branch on status/code.
 */

import { apiUrl, config } from "@/lib/config";
import { tokenStore } from "@/lib/token-store";
import type { ApiErrorBody, TokenPair } from "@/types";

export class ApiError extends Error {
  status: number;
  code?: string;
  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  auth?: boolean; // attach access token (default true)
  form?: URLSearchParams; // for OAuth2 form login
  _retry?: boolean;
}

let refreshInFlight: Promise<boolean> | null = null;

async function tryRefresh(): Promise<boolean> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return false;

  // Collapse concurrent refreshes into one network call.
  refreshInFlight ??= (async () => {
    try {
      const res = await fetch(apiUrl("/auth/refresh"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) return false;
      const tokens: TokenPair = await res.json();
      tokenStore.set(tokens.access_token, tokens.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

export async function apiFetch<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { auth = true, form, body, headers, _retry, ...rest } = opts;

  const finalHeaders = new Headers(headers);
  let payload: BodyInit | undefined;

  if (form) {
    finalHeaders.set("Content-Type", "application/x-www-form-urlencoded");
    payload = form.toString();
  } else if (body !== undefined) {
    finalHeaders.set("Content-Type", "application/json");
    payload = JSON.stringify(body);
  }

  if (auth) {
    const token = tokenStore.getAccess();
    if (token) finalHeaders.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetch(apiUrl(path), { ...rest, headers: finalHeaders, body: payload });

  if (res.status === 401 && auth && !_retry) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return apiFetch<T>(path, { ...opts, _retry: true });
    }
    tokenStore.clear();
  }

  if (!res.ok) {
    let detail = res.statusText;
    let code: string | undefined;
    try {
      const errBody = (await res.json()) as ApiErrorBody;
      detail = errBody.detail ?? detail;
      code = errBody.code;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(detail, res.status, code);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export { config };
