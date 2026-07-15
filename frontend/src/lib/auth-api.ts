/** Auth-related API calls, thin wrappers over `apiFetch`. */

import { apiFetch } from "@/lib/api";
import type { TokenPair, User } from "@/types";

export interface RegisterInput {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

export const authApi = {
  register: (data: RegisterInput) =>
    apiFetch<User>("/auth/register", { method: "POST", body: data, auth: false }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams({ username: email, password });
    return apiFetch<TokenPair>("/auth/login", { method: "POST", form, auth: false });
  },

  me: () => apiFetch<User>("/users/me"),
};
