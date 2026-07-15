/**
 * Framework-agnostic access/refresh token persistence.
 *
 * Kept outside React so the API client can read/refresh tokens without hooks.
 * localStorage is used for simplicity; swap for httpOnly cookies when the
 * backend adds a cookie auth flow (the API surface here stays the same).
 */

const ACCESS_KEY = "pf.access_token";
const REFRESH_KEY = "pf.refresh_token";

const isBrowser = () => typeof window !== "undefined";

export const tokenStore = {
  getAccess(): string | null {
    return isBrowser() ? window.localStorage.getItem(ACCESS_KEY) : null;
  },
  getRefresh(): string | null {
    return isBrowser() ? window.localStorage.getItem(REFRESH_KEY) : null;
  },
  set(access: string, refresh: string): void {
    if (!isBrowser()) return;
    window.localStorage.setItem(ACCESS_KEY, access);
    window.localStorage.setItem(REFRESH_KEY, refresh);
  },
  clear(): void {
    if (!isBrowser()) return;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};
