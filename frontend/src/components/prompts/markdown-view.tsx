"use client";

import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";

/** Renders prompt/markdown content with GFM + syntax-highlighted code blocks. */
export function MarkdownView({ content }: { content: string }) {
  return (
    <div className="prose-pf">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
        {content}
      </ReactMarkdown>
    </div>
  );
}
