import * as http from "http";
import * as https from "https";
import { URL } from "url";

export interface HttpResponse {
  status: number;
  body: Buffer;
}

/** Minimal request using Node's http(s) — avoids depending on a global fetch. */
export function httpRequest(
  urlStr: string,
  method: string,
  headers: Record<string, string>,
  body?: string,
): Promise<HttpResponse> {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const lib = url.protocol === "http:" ? http : https;
    const req = lib.request(url, { method, headers }, (res) => {
      const chunks: Buffer[] = [];
      res.on("data", (c: Buffer) => chunks.push(c));
      res.on("end", () =>
        resolve({ status: res.statusCode ?? 0, body: Buffer.concat(chunks) }),
      );
    });
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

export function httpGet(urlStr: string, headers: Record<string, string>): Promise<HttpResponse> {
  return httpRequest(urlStr, "GET", headers);
}
