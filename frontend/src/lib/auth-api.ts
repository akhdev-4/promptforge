/** Auth-related API calls, thin wrappers over `apiFetch`. */

import { apiFetch } from "@/lib/api";
import type { RecommendationItem, TokenPair, User, UserSuggestion } from "@/types";

export interface RegisterInput {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

export interface ProfileUpdateInput {
  full_name?: string | null;
  username?: string | null;
  bio?: string | null;
  avatar_url?: string | null;
}

export const authApi = {
  register: (data: RegisterInput) =>
    apiFetch<User>("/auth/register", { method: "POST", body: data, auth: false }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    return apiFetch<TokenPair>("/auth/login", { method: "POST", form, auth: false });
  },

  me: () => apiFetch<User>("/users/me"),

  updateMe: (data: ProfileUpdateInput) =>
    apiFetch<User>("/users/me", { method: "PATCH", body: data }),

  recommendations: (limit = 12) =>
    apiFetch<RecommendationItem[]>(`/users/me/recommendations?limit=${limit}`),

  /** Username typeahead (A→Z, excludes you). Empty `q` lists the first page. */
  searchUsers: (q: string, limit = 8) =>
    apiFetch<UserSuggestion[]>(
      `/users/search?limit=${limit}${q ? `&q=${encodeURIComponent(q)}` : ""}`,
    ),
};
