/** Detect what a preview URL points at, so it renders with the right player. */

export type MediaKind = "image" | "video" | "embed";

export interface Media {
  kind: MediaKind;
  /** Player/iframe source (embed URL for hosted video, else the raw URL). */
  src: string;
  /** Poster image when one can be derived (YouTube). */
  poster?: string;
}

const YOUTUBE =
  /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{6,})/;
const VIMEO = /vimeo\.com\/(?:video\/)?(\d+)/;
const LOOM = /loom\.com\/(?:share|embed)\/([A-Za-z0-9]+)/;
const VIDEO_FILE = /\.(mp4|webm|ogg|mov|m4v)(\?.*)?$/i;

export function detectMedia(url: string): Media {
  const clean = url.trim();

  const yt = YOUTUBE.exec(clean);
  if (yt) {
    return {
      kind: "embed",
      src: `https://www.youtube.com/embed/${yt[1]}`,
      poster: `https://img.youtube.com/vi/${yt[1]}/hqdefault.jpg`,
    };
  }
  const vimeo = VIMEO.exec(clean);
  if (vimeo) return { kind: "embed", src: `https://player.vimeo.com/video/${vimeo[1]}` };

  const loom = LOOM.exec(clean);
  if (loom) return { kind: "embed", src: `https://www.loom.com/embed/${loom[1]}` };

  if (VIDEO_FILE.test(clean) || clean.startsWith("data:video/")) {
    return { kind: "video", src: clean };
  }
  return { kind: "image", src: clean };
}

export const isPlayable = (url: string) => detectMedia(url).kind !== "image";
