"use client";

import { ReportCard } from "@/features/reports/ReportCard";
import { TransactionCard } from "@/features/transactions/TransactionCard";
import type { Transaction } from "@/features/transactions/types";
import { renderSimpleMarkdown } from "./markdown";
import type { ChatMessage } from "./types";

type Props = {
  message: ChatMessage;
  onConfirm: (messageId: string, transaction: Transaction) => void;
  onCancel: (messageId: string) => void;
};

export function MessageBubble({ message, onConfirm, onCancel }: Props) {
  const isUser = message.role === "user";

  if (message.type === "transaction" && message.transaction) {
    return (
      <div className="msg" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <AIBubble content={message.content} />
        <div className="card-offset">
          <TransactionCard
            transaction={message.transaction}
            txStatus={message.txStatus}
            onConfirm={(transaction) => onConfirm(message.id, transaction)}
            onCancel={() => onCancel(message.id)}
          />
        </div>
      </div>
    );
  }

  if (message.type === "report" && message.reportData) {
    return (
      <div className="msg" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <AIBubble content={message.content} />
        <div className="card-offset">
          <ReportCard data={message.reportData} />
        </div>
      </div>
    );
  }

  return (
    <div className={`msg msg-row ${isUser ? "user" : ""}`}>
      {!isUser && <FGAvatar />}
      <div className={`bubble ${isUser ? "user" : ""}`}>
        {renderSimpleMarkdown(message.content)}
      </div>
    </div>
  );
}

export function AIBubble({ content }: { content: string }) {
  return (
    <div className="msg-row">
      <FGAvatar />
      <div className="bubble">{renderSimpleMarkdown(content)}</div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="msg msg-row">
      <FGAvatar />
      <div className="typing-bubble">
        {[0, 0.18, 0.36].map((delay) => (
          <span key={delay} className="typing-dot" style={{ animationDelay: `${delay}s` }} />
        ))}
      </div>
    </div>
  );
}

export function FGAvatar() {
  return <div className="avatar">FG</div>;
}
