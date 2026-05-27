"use client";

import { ReportCard } from "@/features/reports/ReportCard";
import { TransactionCard } from "@/features/transactions/TransactionCard";
import type { Transaction, TransactionStatus } from "@/features/transactions/types";
import { renderSimpleMarkdown } from "./markdown";
import type { ChatMessage } from "./types";

type Props = {
  message: ChatMessage;
  transactions: Transaction[];
  onConfirm: (messageId: string, transaction: Transaction) => void;
  onCancel: (messageId: string) => void;
  onRetry?: () => void;
};

function resolveTxStatus(message: ChatMessage, transactions: Transaction[]): TransactionStatus {
  if (message.txStatus === "confirmed" || message.txStatus === "discarded") {
    return message.txStatus;
  }
  const id = message.transaction?.id;
  if (!id) return "pending_confirmation";
  const row = transactions.find((tx) => tx.id === id);
  return row?.status ?? message.txStatus ?? "pending_confirmation";
}

export function MessageBubble({ message, transactions, onConfirm, onCancel, onRetry }: Props) {
  const isUser = message.role === "user";

  if (message.type === "transaction" && message.transaction) {
    const txStatus = resolveTxStatus(message, transactions);
    return (
      <div className="msg" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <AIBubble content={message.content} />
        <div className="card-offset">
          <TransactionCard
            transaction={message.transaction}
            txStatus={txStatus}
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

  if (message.type === "error") {
    return (
      <div className="msg msg-row">
        <FGAvatar />
        <div className="bubble error-bubble">
          {renderSimpleMarkdown(message.content)}
          {onRetry && (
            <button type="button" className="button button-ghost" onClick={onRetry}>
              Retry
            </button>
          )}
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
