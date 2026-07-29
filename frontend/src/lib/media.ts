/** Detect what a preview URL points at, so it renders with the right player. */

export type MediaKind = "image" | "video" | "embed";

export interface Media {
  kind: MediaKind;
  /** Player/iframe source (embed URL for hosted video, else the raw URL). */
  src: string;
  /** Poster image when one can be derived (YouTube). */
  poster?: string;
  /**
   * Silent, looping, chrome-less variant used for the inline grid preview.
   * Muting is what makes browsers allow autoplay at all.
   */
  autoplaySrc?: string;
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
    const id = yt[1];
    return {
      kind: "embed",
      src: `https://www.youtube.com/embed/${id}`,
      poster: `https://img.youtube.com/vi/${id}/hqdefault.jpg`,
      // YouTube needs `playlist` set to the same id for `loop` to work.
      autoplaySrc:
        `https://www.youtube.com/embed/${id}?autoplay=1&mute=1&loop=1&playlist=${id}` +
        "&controls=0&modestbranding=1&playsinline=1&rel=0",
    };
  }
  const vimeo = VIMEO.exec(clean);
  if (vimeo) {
    return {
      kind: "embed",
      src: `https://player.vimeo.com/video/${vimeo[1]}`,
      // `background=1` is Vimeo's built-in silent, looping, control-less mode.
      autoplaySrc: `https://player.vimeo.com/video/${vimeo[1]}?background=1&autoplay=1&loop=1&muted=1`,
    };
  }

  const loom = LOOM.exec(clean);
  if (loom) {
    return {
      kind: "embed",
      src: `https://www.loom.com/embed/${loom[1]}`,
      autoplaySrc:
        `https://www.loom.com/embed/${loom[1]}?autoplay=1&muted=true` +
        "&hideEmbedTopBar=true&hide_owner=true&hide_share=true&hide_title=true",
    };
  }

  if (VIDEO_FILE.test(clean) || clean.startsWith("data:video/")) {
    return { kind: "video", src: clean };
  }
  return { kind: "image", src: clean };
}

export const isPlayable = (url: string) => detectMedia(url).kind !== "image";
