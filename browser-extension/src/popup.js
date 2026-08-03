import { api, getConfig } from "./api.js";

const $ = (id) => document.getElementById(id);

/** Derive a sensible title from the first meaningful line of the prompt. */
function titleFrom(text) {
  const line = text.trim().split("\n").find((l) => l.trim()) ?? "";
  return line.trim().replace(/^["'#\-*\s]+/, "").slice(0, 80);
}

/** Read the user's current selection from the active tab. */
async function selectionFromPage() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) return "";
    const [hit] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.getSelection()?.toString() ?? "",
    });
    return hit?.result ?? "";
  } catch {
    // Restricted pages (chrome://, the Web Store) can't be scripted — fine.
    return "";
  }
}

function setStatus(el, message, kind = "") {
  el.textContent = message;
  el.className = `status ${kind}`;
}

// --- Tabs -------------------------------------------------------------------
function activate(which) {
  const save = which === "save";
  $("tab-save").setAttribute("aria-selected", String(save));
  $("tab-find").setAttribute("aria-selected", String(!save));
  $("panel-save").classList.toggle("active", save);
  $("panel-find").classList.toggle("active", !save);
}
$("tab-save").addEventListener("click", () => activate("save"));
$("tab-find").addEventListener("click", () => activate("find"));

const openOptions = (e) => {
  e?.preventDefault();
  chrome.runtime.openOptionsPage();
};
$("open-options").addEventListener("click", openOptions);
$("go-options").addEventListener("click", openOptions);

// --- Save -------------------------------------------------------------------
$("save").addEventListener("click", async () => {
  const content = $("content").value.trim();
  const status = $("save-status");
  if (!content) return setStatus(status, "Add some prompt text first.", "error");

  const title = $("title").value.trim() || titleFrom(content);
  $("save").disabled = true;
  setStatus(status, "Saving…");
  try {
    const saved = await api.publish({ title, content, prompt_type: $("type").value });
    const { apiUrl } = await getConfig();
    status.className = "status ok";
    status.textContent = "Saved. ";
    const link = document.createElement("a");
    link.href = `${apiUrl}/prompts/${saved.id}`;
    link.target = "_blank";
    link.textContent = "Open in PromptForge";
    status.append(link);
    $("content").value = "";
    $("title").value = "";
  } catch (err) {
    setStatus(status, err.message, "error");
  } finally {
    $("save").disabled = false;
  }
});

// Auto-fill the title from the prompt while it's still untouched by the user.
let titleEdited = false;
$("title").addEventListener("input", () => {
  titleEdited = true;
});
$("content").addEventListener("input", () => {
  if (!titleEdited) $("title").value = titleFrom($("content").value);
});

// --- Find -------------------------------------------------------------------
let searchTimer;
$("query").addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(runSearch, 250);
});

async function runSearch() {
  const query = $("query").value.trim();
  const status = $("find-status");
  const results = $("results");
  results.replaceChildren();
  if (!query) return setStatus(status, "");

  setStatus(status, "Searching…");
  try {
    const page = await api.search(query);
    const items = page.items ?? [];
    setStatus(status, items.length ? "" : "No prompts matched.");
    for (const prompt of items) {
      const button = document.createElement("button");
      button.className = "result";
      const strong = document.createElement("strong");
      strong.textContent = prompt.title;
      const span = document.createElement("span");
      span.textContent = prompt.description || prompt.prompt_type || "";
      button.append(strong, span);
      button.addEventListener("click", () => copyPrompt(prompt.id, status));
      results.append(button);
    }
  } catch (err) {
    setStatus(status, err.message, "error");
  }
}

async function copyPrompt(id, status) {
  setStatus(status, "Fetching…");
  try {
    const detail = await api.get(id);
    await navigator.clipboard.writeText(detail.content);
    setStatus(status, "Copied to clipboard — paste it into the chat.", "ok");
  } catch (err) {
    setStatus(status, err.message, "error");
  }
}

// --- Boot -------------------------------------------------------------------
(async () => {
  const { apiKey } = await getConfig();
  if (!apiKey) return; // leave the setup panel showing
  $("setup").classList.remove("active");
  $("main").hidden = false;

  // A pending capture from the context menu wins over the live selection.
  const { pendingCapture } = await chrome.storage.local.get("pendingCapture");
  const text = pendingCapture || (await selectionFromPage());
  if (pendingCapture) await chrome.storage.local.remove("pendingCapture");
  if (text) {
    $("content").value = text;
    $("title").value = titleFrom(text);
  }
})();
