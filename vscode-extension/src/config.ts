import * as vscode from "vscode";

const SECRET_KEY = "promptforge.apiKey";
const DEFAULT_API_URL = "https://promptforge.fastapicloud.dev";

export function getApiUrl(): string {
  const configured = vscode.workspace
    .getConfiguration("promptforge")
    .get<string>("apiUrl");
  return (configured || DEFAULT_API_URL).replace(/\/+$/, "");
}

export function getApiKey(context: vscode.ExtensionContext): Thenable<string | undefined> {
  return context.secrets.get(SECRET_KEY);
}

export function setApiKey(context: vscode.ExtensionContext, key: string): Thenable<void> {
  return context.secrets.store(SECRET_KEY, key);
}
