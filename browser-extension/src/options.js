import { DEFAULT_API_URL, getConfig, setConfig, verify } from "./api.js";

const $ = (id) => document.getElementById(id);

function setStatus(message, kind = "") {
  $("status").textContent = message;
  $("status").className = `status ${kind}`;
}

/**
 * Only the default host is granted in the manifest, so a custom URL needs the
 * user's consent before fetch() is allowed to reach it.
 */
async function ensureHostAccess(apiUrl) {
  const origin = `${new URL(apiUrl).origin}/*`;
  if (await chrome.permissions.contains({ origins: [origin] })) return true;
  return chrome.permissions.request({ origins: [origin] });
}

$("save").addEventListener("click", async () => {
  const apiUrl = ($("apiUrl").value.trim() || DEFAULT_API_URL).replace(/\/+$/, "");
  const apiKey = $("apiKey").value.trim();
  if (!apiKey) return setStatus("Paste your API key first.", "error");

  let origin;
  try {
    origin = new URL(apiUrl).origin;
  } catch {
    return setStatus("That URL doesn't look right.", "error");
  }

  $("save").disabled = true;
  setStatus("Verifying…");
  try {
    if (!(await ensureHostAccess(apiUrl))) {
      return setStatus(`Permission to reach ${origin} was declined.`, "error");
    }
    const me = await verify(apiUrl, apiKey);
    await setConfig(apiUrl, apiKey);
    setStatus(`Connected as @${me.username ?? me.full_name ?? "you"}.`, "ok");
  } catch (err) {
    setStatus(err.message, "error");
  } finally {
    $("save").disabled = false;
  }
});

(async () => {
  const { apiUrl, apiKey } = await getConfig();
  $("apiUrl").value = apiUrl;
  $("apiKey").value = apiKey;
})();
