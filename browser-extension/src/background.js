import { api, getConfig } from "./api.js";

const QUICK_SAVE = "promptforge-quick-save";
const REVIEW = "promptforge-review";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: QUICK_SAVE,
      title: "Save selection to PromptForge",
      contexts: ["selection"],
    });
    chrome.contextMenus.create({
      id: REVIEW,
      title: "Save selection… (add a title first)",
      contexts: ["selection"],
    });
  });
});

function notify(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: chrome.runtime.getURL("icons/icon128.png"),
    title,
    message,
  });
}

/** First meaningful line, trimmed of markdown noise — mirrors the popup. */
function titleFrom(text) {
  const line = text.trim().split("\n").find((l) => l.trim()) ?? "";
  return line.trim().replace(/^["'#\-*\s]+/, "").slice(0, 80) || "Untitled prompt";
}

chrome.contextMenus.onClicked.addListener(async (info) => {
  const content = (info.selectionText ?? "").trim();
  if (!content) return;

  const { apiKey } = await getConfig();
  if (!apiKey) {
    notify("PromptForge", "Add your API key in the extension options first.");
    chrome.runtime.openOptionsPage();
    return;
  }

  if (info.menuItemId === REVIEW) {
    // Hand off to the popup: the toolbar popup can't be opened programmatically
    // in a way that's reliable across versions, so we stash it and say so.
    await chrome.storage.local.set({ pendingCapture: content });
    notify("PromptForge", "Captured — click the PromptForge icon to finish saving.");
    return;
  }

  if (info.menuItemId !== QUICK_SAVE) return;
  try {
    await api.publish({
      title: titleFrom(content),
      content,
      prompt_type: "other",
    });
    notify("Saved to PromptForge", titleFrom(content));
  } catch (err) {
    notify("Couldn't save", err.message);
  }
});
