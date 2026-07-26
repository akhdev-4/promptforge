import * as fs from "fs";
import * as path from "path";

import * as vscode from "vscode";

import { Api, ApiError, Identity, Kit, KitManifest, PromptDetail, PromptSummary } from "./api";
import { extractZipStripped } from "./archive";
import { setApiKey } from "./config";
import { KitTreeItem } from "./kitsTree";

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

export async function setApiKeyCommand(
  context: vscode.ExtensionContext,
  api: Api,
): Promise<void> {
  const key = await vscode.window.showInputBox({
    prompt: "Paste your PromptForge API key (Settings → API keys)",
    password: true,
    ignoreFocusOut: true,
  });
  if (!key) return;
  await setApiKey(context, key.trim());
  try {
    const me = await api.get<Identity>("/me");
    vscode.window.showInformationMessage(`PromptForge: signed in as @${me.username}`);
  } catch (err) {
    vscode.window.showErrorMessage(`Key saved, but verification failed: ${errorMessage(err)}`);
  }
}

export async function whoamiCommand(api: Api): Promise<void> {
  try {
    const me = await api.get<Identity>("/me");
    vscode.window.showInformationMessage(
      `PromptForge: @${me.username} (${me.role})`,
    );
  } catch (err) {
    vscode.window.showErrorMessage(errorMessage(err));
  }
}

async function chooseKit(api: Api): Promise<Kit | undefined> {
  const page = await api.get<{ items: Kit[] }>("/templates");
  if (!page.items.length) {
    vscode.window.showInformationMessage("No starter kits available.");
    return undefined;
  }
  const picked = await vscode.window.showQuickPick(
    page.items.map((kit) => ({
      label: kit.name,
      description: [kit.category, kit.stack].filter(Boolean).join(" · "),
      detail: kit.description ?? undefined,
      kit,
    })),
    { placeHolder: "Select a starter kit to pull" },
  );
  return picked?.kit;
}

export async function pullKitCommand(api: Api, item?: KitTreeItem): Promise<void> {
  const kit = item?.kit ?? (await chooseKit(api));
  if (!kit) return;

  // Default the destination to the first workspace folder, if any.
  const defaultParent = vscode.workspace.workspaceFolders?.[0]?.uri;
  const picked = await vscode.window.showOpenDialog({
    canSelectFolders: true,
    canSelectFiles: false,
    canSelectMany: false,
    openLabel: "Pull here",
    title: "Choose a folder to pull the kit into",
    defaultUri: defaultParent,
  });
  if (!picked || picked.length === 0) return;

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: `Pulling ${kit.name}…` },
    async (progress) => {
      try {
        progress.report({ message: "Fetching manifest" });
        const manifest = await api.get<KitManifest>(`/templates/${kit.project_id}`);
        const target = path.join(picked[0].fsPath, manifest.slug);

        if (fs.existsSync(target) && fs.readdirSync(target).length > 0) {
          const answer = await vscode.window.showWarningMessage(
            `${target} isn't empty. Overwrite its contents?`,
            { modal: true },
            "Overwrite",
          );
          if (answer !== "Overwrite") return;
        }

        progress.report({ message: "Downloading codebase" });
        const zip = await api.downloadZip(`/templates/${kit.project_id}/download`);

        progress.report({ message: "Unpacking" });
        fs.mkdirSync(target, { recursive: true });
        extractZipStripped(zip, target);
        writePromptsDoc(target, manifest);

        const open = await vscode.window.showInformationMessage(
          `Pulled ${kit.name} (${manifest.prompt_count} prompts). ` +
            (manifest.setup_command ? `Next: ${manifest.setup_command}` : ""),
          "Open Folder",
        );
        if (open === "Open Folder") {
          await vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(target), {
            forceNewWindow: true,
          });
        }
      } catch (err) {
        vscode.window.showErrorMessage(`Pull failed: ${errorMessage(err)}`);
      }
    },
  );
}

function writePromptsDoc(target: string, manifest: KitManifest): void {
  const lines: string[] = [
    `# ${manifest.name} — prompts`,
    "",
    (manifest.description ?? "").trim(),
    "",
    `Pulled from PromptForge. Stack: ${manifest.stack ?? "n/a"}.`,
    "",
  ];
  for (const module of manifest.modules) {
    lines.push(`## ${module.name}`);
    for (const comp of module.components) {
      lines.push(`### ${comp.name}`);
      for (const prompt of comp.prompts) {
        lines.push(`- ${prompt.title}  \`${prompt.id}\``);
      }
    }
    lines.push("");
  }
  fs.writeFileSync(path.join(target, "PROMPTFORGE.md"), lines.join("\n"), "utf-8");
}

export async function searchPromptsCommand(api: Api): Promise<void> {
  const query = await vscode.window.showInputBox({
    prompt: "Search PromptForge prompts",
    ignoreFocusOut: true,
  });
  if (!query) return;

  let page: { items: PromptSummary[] };
  try {
    page = await api.get<{ items: PromptSummary[] }>(
      `/prompts?q=${encodeURIComponent(query)}&size=20`,
    );
  } catch (err) {
    vscode.window.showErrorMessage(errorMessage(err));
    return;
  }
  if (!page.items.length) {
    vscode.window.showInformationMessage("No prompts matched.");
    return;
  }

  const picked = await vscode.window.showQuickPick(
    page.items.map((p) => ({
      label: p.title,
      description: p.prompt_type ?? undefined,
      detail: p.description ?? undefined,
      id: p.id,
    })),
    { placeHolder: "Select a prompt to insert" },
  );
  if (!picked) return;

  try {
    const detail = await api.get<PromptDetail>(`/prompts/${picked.id}`);
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      await editor.edit((builder) => builder.insert(editor.selection.active, detail.content));
    } else {
      const doc = await vscode.workspace.openTextDocument({
        content: detail.content,
        language: "markdown",
      });
      await vscode.window.showTextDocument(doc);
    }
  } catch (err) {
    if (err instanceof ApiError) {
      vscode.window.showErrorMessage(err.message);
    } else {
      vscode.window.showErrorMessage(errorMessage(err));
    }
  }
}
