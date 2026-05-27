import type { ReactNode } from "react";

/** Escape text before injecting into React children (FE-6). */
function escapeText(text: string): string {
  return text.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

export function renderSimpleMarkdown(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const lines = text.split("\n");

  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) nodes.push(<br key={`br-${lineIndex}`} />);

    const bullet = line.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      nodes.push(
        <span
          key={`bullet-${lineIndex}`}
          style={{ display: "block", paddingLeft: 12, position: "relative" }}
        >
          <span style={{ left: 0, position: "absolute" }}>*</span>
          {renderInline(bullet[1] ?? "")}
        </span>,
      );
      return;
    }

    nodes.push(<span key={`line-${lineIndex}`}>{renderInline(line)}</span>);
  });

  return nodes;
}

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{escapeText(part.slice(2, -2))}</strong>;
    }

    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={index}>{escapeText(part.slice(1, -1))}</em>;
    }

    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{escapeText(part.slice(1, -1))}</code>;
    }

    return escapeText(part);
  });
}
