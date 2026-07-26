# PromptForge for VS Code

Browse **PromptForge starter kits** and **prompts** without leaving the editor —
and pull a full starter codebase straight into your workspace.

## Features

- **Starter Kits** view in the activity bar — lists kits from your PromptForge.
- **Pull Kit into Workspace** — downloads the codebase (streamed through
  PromptForge), unpacks it into a folder you choose, and drops a `PROMPTFORGE.md`
  listing the prompts behind the kit.
- **Search Prompts** — find a published prompt and insert its content into the
  active editor (or open it in a new document).
- Your API key is stored securely in VS Code **SecretStorage**.

## Setup

1. Create an API key in PromptForge (**Settings → API keys**).
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
| `PromptForge: Refresh Kits` | Reload the Starter Kits view |

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

Access is read-only and limited to published, public prompts/kits.
