# PromptForge — browser extension

Capture prompts from any AI chat into your PromptForge library, and pull your saved
prompts back out without leaving the page.

Most people's best prompts are stranded in chat history. This closes that loop.

## Features

- **Save selection** — highlight a prompt in ChatGPT, Claude, Gemini (or anywhere),
  then save it from the popup with a title and type.
- **Right-click quick save** — *Save selection to PromptForge* publishes immediately
  with a title derived from the first line. *Save selection…* hands it to the popup
  so you can edit it first.
- **Find** — search your library and copy a prompt's full text to the clipboard,
  ready to paste into the chat.
- The popup pre-fills with whatever you have selected on the page.

## Install (unpacked)

1. Open `chrome://extensions` and turn on **Developer mode**.
2. **Load unpacked** → select this `browser-extension/` folder.
3. Click the PromptForge icon → **Open options**.

Works in Chrome, Edge, Brave and other Chromium browsers.

## Connect it

1. In PromptForge, go to **Settings → API keys**.
2. Tick **“Allow publishing (write access)”** — a read-only key can search but not save.
3. Create the key, copy the secret, and paste it into the extension's options.
4. Press **Verify & save** — it checks the key against the server before storing it.

Pointing at a different server (e.g. `http://localhost:8000`) is supported; the
extension asks for permission to reach that origin the first time.

## Permissions, and why

| Permission | Why |
|---|---|
| `storage` | Remember your API URL and key on this device |
| `contextMenus` | The right-click "Save selection" items |
| `activeTab` + `scripting` | Read the text you've selected, only when you open the popup |
| `notifications` | Report the result of a right-click quick save |
| host access | Talk to your PromptForge server — the default host only, unless you point it elsewhere |

The extension reads **only your current selection**, and only when you ask it to. It
never scrapes page content in the background, and the key is sent to nowhere except
the PromptForge URL you configured.

## Notes

- Saving requires a **write-scoped** key; searching works with any key.
- Access is limited to published, public prompts — the same rules as the API.
- Browsers block extensions from running on a few pages (`chrome://`, the Web Store),
  so selection capture won't work there. Pasting into the popup still does.
