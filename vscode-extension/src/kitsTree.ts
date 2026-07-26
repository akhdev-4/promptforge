import * as vscode from "vscode";

import { Api, Kit } from "./api";

export class KitTreeItem extends vscode.TreeItem {
  constructor(public readonly kit: Kit) {
    super(kit.name, vscode.TreeItemCollapsibleState.None);
    this.description = [kit.category, kit.stack].filter(Boolean).join(" · ");
    this.tooltip = `${kit.prompt_count} prompt(s)\n${kit.description ?? ""}`.trim();
    this.contextValue = "kit";
    this.iconPath = new vscode.ThemeIcon("package");
    this.command = {
      command: "promptforge.pullKit",
      title: "Pull Kit into Workspace",
      arguments: [this],
    };
  }
}

/** A non-kit row used for empty/error states (no context actions). */
class InfoItem extends vscode.TreeItem {
  constructor(label: string) {
    super(label, vscode.TreeItemCollapsibleState.None);
    this.contextValue = "info";
  }
}

export class KitsProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
  private readonly _onDidChange = new vscode.EventEmitter<void>();
  readonly onDidChangeTreeData = this._onDidChange.event;

  constructor(private readonly api: Api) {}

  refresh(): void {
    this._onDidChange.fire();
  }

  getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
    return element;
  }

  async getChildren(): Promise<vscode.TreeItem[]> {
    try {
      const page = await this.api.get<{ items: Kit[] }>("/templates");
      if (!page.items.length) {
        return [new InfoItem("No starter kits found.")];
      }
      return page.items.map((kit) => new KitTreeItem(kit));
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      return [new InfoItem(message)];
    }
  }
}
