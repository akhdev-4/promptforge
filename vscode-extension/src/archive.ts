import * as fs from "fs";
import * as path from "path";

import AdmZip from "adm-zip";

/**
 * Extract a zip buffer into ``target``, stripping the single top-level folder
 * that GitHub archives wrap everything in.
 */
export function extractZipStripped(zipBuffer: Buffer, target: string): void {
  const zip = new AdmZip(zipBuffer);
  const entries = zip.getEntries();
  if (entries.length === 0) return;

  // GitHub archives share one "<repo>-<ref>/" prefix; detect and drop it.
  const first = entries[0].entryName;
  const slashIndex = first.indexOf("/");
  const prefix = slashIndex > 0 ? first.slice(0, slashIndex + 1) : "";

  for (const entry of entries) {
    if (entry.isDirectory) continue;
    const relative =
      prefix && entry.entryName.startsWith(prefix)
        ? entry.entryName.slice(prefix.length)
        : entry.entryName;
    if (!relative) continue;
    const dest = path.join(target, relative);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, entry.getData());
  }
}
