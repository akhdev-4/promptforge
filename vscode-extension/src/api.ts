import * as vscode from "vscode";

import { getApiKey, getApiUrl } from "./config";
import { httpGet } from "./http";

export class ApiError extends Error {}

export interface Kit {
  project_id: string;
  name: string;
  description: string | null;
  category: string | null;
  stack: string | null;
  prompt_count: number;
}

export interface ManifestPrompt {
  id: string;
  slug: string;
  title: string;
}
export interface ManifestComponent {
  name: string;
  prompts: ManifestPrompt[];
}
export interface ManifestModule {
  name: string;
  components: ManifestComponent[];
}
export interface KitManifest extends Kit {
  slug: string;
  setup_command: string | null;
  modules: ManifestModule[];
}

export interface PromptSummary {
  id: string;
  title: string;
  description: string | null;
  prompt_type: string | null;
}
export interface PromptDetail extends PromptSummary {
  content: string;
}

export interface Identity {
  username: string | null;
  full_name: string | null;
  role: string;
}

export class Api {
  constructor(private readonly context: vscode.ExtensionContext) {}

  private base(): string {
    return `${getApiUrl()}/api/v1/public`;
  }

  private async headers(): Promise<Record<string, string>> {
    const key = await getApiKey(this.context);
    if (!key) {
      throw new ApiError("No API key set. Run 'PromptForge: Set API Key'.");
    }
    return { "X-API-Key": key };
  }

  private explain(status: number): string {
    if (status === 401) return "Invalid or revoked API key.";
    if (status === 404) return "Not found.";
    if (status === 429) return "Rate limited — please slow down.";
    return `Request failed (${status}).`;
  }

  async get<T>(path: string): Promise<T> {
    const res = await httpGet(`${this.base()}${path}`, await this.headers());
    if (res.status < 200 || res.status >= 300) {
      throw new ApiError(this.explain(res.status));
    }
    return JSON.parse(res.body.toString("utf-8")) as T;
  }

  async downloadZip(path: string): Promise<Buffer> {
    const res = await httpGet(`${this.base()}${path}`, await this.headers());
    if (res.status < 200 || res.status >= 300) {
      throw new ApiError(this.explain(res.status));
    }
    return res.body;
  }
}
