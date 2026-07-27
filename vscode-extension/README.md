# PromptForge for VS Code

Browse **PromptForge starter kits** and **prompts**, pull a full starter codebase
into your workspace, and **publish prompts back to PromptForge** — all without
leaving the editor.

## Features

- **Starter Kits** view in the activity bar — lists kits from your PromptForge.
- **Pull Kit into Workspace** — downloads the codebase (streamed through
  PromptForge), unpacks it into a folder you choose, and drops a `PROMPTFORGE.md`
  listing the prompts behind the kit.
- **Search Prompts** — find a published prompt and insert its content into the
  active editor (or open it in a new document).
- **Publish Selection as Prompt** — select text (or use the whole file) and
  publish it to PromptForge as a new prompt. Requires a **write-scoped** API key.
- Your API key is stored securely in VS Code **SecretStorage**.

## Setup

1. Create an API key in PromptForge (**Settings → API keys**). Keys are
   **read-only by default** — tick **"Allow publishing"** if you want to publish
   prompts from the editor.
2. Run **PromptForge: Set API Key** (Command Palette) and paste it.
3. Open the **PromptForge** view in the activity bar.

Point at a different server with the `promptforge.apiUrl` setting
(default `https://promptforge.fastapicloud.dev`).

## Commands

| Command | What it does |
|---|---|
| `PromptForge: Set API Key` | Store + verify your key |
| `PromptForge: Who Am I` | Show the account behind the key |
| `PromptForge: Pull Kit into Workspace` | Download a kit's codebase |
| `PromptForge: Search Prompts` | Find and insert a prompt |
| `PromptForge: Publish Selection as Prompt` | Publish the selection/file as a new prompt (needs a write-scoped key) |
| `PromptForge: Refresh Kits` | Reload the Starter Kits view |

You can also **right-click a selection** in the editor → *PromptForge: Publish
Selection as Prompt*.

## Access & safety

Reading (kits, prompts) works with any key. **Publishing** requires a key you
explicitly created with write access, so a leaked read-only key can never create,
edit, or delete anything. Access is limited to published, public content.

## Develop

```bash
npm install
npm run compile        # or: npm run watch
# press F5 in VS Code to launch an Extension Development Host
```

Package a `.vsix` with [`@vscode/vsce`](https://github.com/microsoft/vscode-vsce):

```bash
npx @vscode/vsce package
```
