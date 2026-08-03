/** Thin client for the PromptForge public API, shared by popup/options/background. */

const DEFAULT_API_URL = "https://promptforge.fastapicloud.dev";

export async function getConfig() {
  const { apiUrl, apiKey } = await chrome.storage.local.get(["apiUrl", "apiKey"]);
  return {
    apiUrl: (apiUrl || DEFAULT_API_URL).replace(/\/+$/, ""),
    apiKey: apiKey || "",
  };
}

export async function setConfig(apiUrl, apiKey) {
  await chrome.storage.local.set({
    apiUrl: (apiUrl || DEFAULT_API_URL).replace(/\/+$/, ""),
    apiKey,
  });
}

export { DEFAULT_API_URL };

/** Turn a failed response into a message worth showing a human. */
async function explain(res) {
  if (res.status === 401) return "Invalid or revoked API key. Check it in Options.";
  if (res.status === 403) {
    return "This key is read-only. Create one with “Allow publishing” ticked in PromptForge → Settings → API keys.";
  }
  if (res.status === 429) return "Rate limited — wait a moment and try again.";
  try {
    const body = await res.json();
    if (body?.detail) return String(body.detail);
  } catch {
    /* fall through to the generic message */
  }
  return `Request failed (${res.status}).`;
}

async function request(path, options = {}) {
  const { apiUrl, apiKey } = await getConfig();
  if (!apiKey) throw new Error("No API key set yet — open Options to add one.");

  let res;
  try {
    res = await fetch(`${apiUrl}/api/v1/public${path}`, {
      ...options,
      headers: {
        "X-API-Key": apiKey,
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new Error(`Couldn't reach ${apiUrl}. Is the URL right and the server up?`);
  }
  if (!res.ok) throw new Error(await explain(res));
  return res.status === 204 ? null : res.json();
}

export const api = {
  whoami: () => request("/me"),

  publish: (prompt) =>
    request("/prompts", { method: "POST", body: JSON.stringify(prompt) }),

  search: (query, limit = 8) =>
    request(`/prompts?q=${encodeURIComponent(query)}&size=${limit}`),

  get: (id) => request(`/prompts/${id}`),
};

/** Verify a key/URL pair before saving it (bypasses stored config). */
export async function verify(apiUrl, apiKey) {
  const base = (apiUrl || DEFAULT_API_URL).replace(/\/+$/, "");
  const res = await fetch(`${base}/api/v1/public/me`, {
    headers: { "X-API-Key": apiKey },
  });
  if (!res.ok) throw new Error(await explain(res));
  return res.json();
}
