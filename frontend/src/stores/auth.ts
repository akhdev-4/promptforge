/** Global auth state (zustand). Holds the current user + auth lifecycle. */

import { create } from "zustand";

import { ApiError } from "@/lib/api";
import { authApi, type RegisterInput } from "@/lib/auth-api";
import { tokenStore } from "@/lib/token-store";
import type { User } from "@/types";

interface AuthState {
  user: User | null;
  status: "idle" | "loading" | "authenticated" | "unauthenticated";
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterInput) => Promise<void>;
  logout: () => void;
  /** Restore session on app load using a stored token. */
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  status: "idle",

  login: async (email, password) => {
    const tokens = await authApi.login(email, password);
    tokenStore.set(tokens.access_token, tokens.refresh_token);
    const user = await authApi.me();
    set({ user, status: "authenticated" });
  },

  register: async (data) => {
    await authApi.register(data);
    // Auto-login after successful registration.
    const tokens = await authApi.login(data.email, data.password);
    tokenStore.set(tokens.access_token, tokens.refresh_token);
    const user = await authApi.me();
    set({ user, status: "authenticated" });
  },

  logout: () => {
    tokenStore.clear();
    set({ user: null, status: "unauthenticated" });
  },

  hydrate: async () => {
    if (!tokenStore.getAccess()) {
      set({ status: "unauthenticated" });
      return;
    }
    set({ status: "loading" });
    try {
      const user = await authApi.me();
      set({ user, status: "authenticated" });
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) tokenStore.clear();
      set({ user: null, status: "unauthenticated" });
    }
  },
}));
