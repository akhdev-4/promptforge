"use client";

import * as React from "react";

interface SRResult {
  readonly [index: number]: { transcript: string };
  length: number;
  isFinal: boolean;
}
interface SREvent {
  results: { readonly [index: number]: SRResult; length: number };
}
interface SR {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((e: SREvent) => void) | null;
  onerror: ((e: { error?: string }) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

function getRecognitionCtor(): (new () => SR) | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as {
    SpeechRecognition?: new () => SR;
    webkitSpeechRecognition?: new () => SR;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

function friendlyError(code?: string): string {
  switch (code) {
    case "not-allowed":
    case "service-not-allowed":
      return "Microphone access is blocked. Allow it for this site, then try again.";
    case "no-speech":
      return "Didn't catch that — tap the mic and try again.";
    case "audio-capture":
      return "No microphone found.";
    case "network":
      return "Network issue with voice recognition — try again.";
    case "aborted":
      return "";
    default:
      return "Voice input didn't work. Try again.";
  }
}

/**
 * Browser-native speech→text (no key/backend). `onResult` fires repeatedly with
 * the growing transcript; `isFinal` is true on the last chunk of an utterance.
 */
export function useSpeechRecognition(onResult: (text: string, isFinal: boolean) => void) {
  const [supported, setSupported] = React.useState(false);
  const [listening, setListening] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const recRef = React.useRef<SR | null>(null);
  const onResultRef = React.useRef(onResult);
  onResultRef.current = onResult;

  React.useEffect(() => {
    setSupported(getRecognitionCtor() !== null);
    return () => recRef.current?.abort();
  }, []);

  const start = React.useCallback(() => {
    const Ctor = getRecognitionCtor();
    if (!Ctor) return;
    recRef.current?.abort();
    setError(null);

    const rec = new Ctor();
    rec.lang = navigator.language || "en-US";
    rec.interimResults = true; // stream partial text as the user speaks
    rec.continuous = false;
    rec.maxAlternatives = 1;

    rec.onstart = () => setListening(true);
    rec.onresult = (e) => {
      let text = "";
      let isFinal = false;
      for (let i = 0; i < e.results.length; i++) {
        const r = e.results[i]!;
        text += r[0]!.transcript;
        if (r.isFinal) isFinal = true;
      }
      onResultRef.current(text.trim(), isFinal);
    };
    rec.onerror = (e) => {
      const msg = friendlyError(e?.error);
      if (msg) setError(msg);
      setListening(false);
    };
    rec.onend = () => setListening(false);

    recRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch {
      setListening(false);
    }
  }, []);

  const stop = React.useCallback(() => {
    recRef.current?.stop();
    setListening(false);
  }, []);

  return { supported, listening, error, start, stop };
}
