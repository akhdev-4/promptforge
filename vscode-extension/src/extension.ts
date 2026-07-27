import * as vscode from "vscode";

import { Api } from "./api";
import {
  publishPromptCommand,
  pullKitCommand,
  searchPromptsCommand,
  setApiKeyCommand,
  whoamiCommand,
} from "./commands";
import { KitsProvider, KitTreeItem } from "./kitsTree";

export function activate(context: vscode.ExtensionContext): void {
  const api = new Api(context);
  const kitsProvider = new KitsProvider(api);

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider("promptforgeKits", kitsProvider),
    vscode.commands.registerCommand("promptforge.setApiKey", async () => {
      await setApiKeyCommand(context, api);
      kitsProvider.refresh();
    }),
    vscode.commands.registerCommand("promptforge.whoami", () => whoamiCommand(api)),
    vscode.commands.registerCommand("promptforge.refreshKits", () => kitsProvider.refresh()),
    vscode.commands.registerCommand("promptforge.pullKit", (item?: KitTreeItem) =>
      pullKitCommand(api, item),
    ),
    vscode.commands.registerCommand("promptforge.searchPrompts", () =>
      searchPromptsCommand(api),
    ),
    vscode.commands.registerCommand("promptforge.publishPrompt", () =>
      publishPromptCommand(api),
    ),
  );
}

export function deactivate(): void {
  /* nothing to clean up */
}
