"use client";

import { DashboardPanel } from "@/features/reports/DashboardPanel";
import type { Transaction } from "@/features/transactions/types";
import { todayISO } from "@/lib/format";
import type { ChatApiResponse } from "@/server/chat/schemas";
import { useEffect, useMemo, useRef, useState } from "react";
import { InputBar } from "./InputBar";
import { MessageBubble, TypingIndicator } from "./MessageBubble";
import { mapApiMessagesToChat } from "./map-api-messages";
import type { ChatMessage } from "./types";

const storageKeys = {
  messages: "fg_next_msgs",
  transactions: "fg_next_txs",
};

const welcomeMessage: ChatMessage = {
  id: "welcome",
  role: "assistant",
  type: "text",
  content:
    'Hi! I\'m **Finguard**, your AI financial assistant.\n\nTell me about your finances in plain language:\n- *"I got paid $3,200 today"*\n- *"Spent $45 on groceries"*\n- *"Show me my spending report"*\n\nI\'ll record transactions for you to confirm, and summarize your spending when you ask.',
  timestamp: "initial",
};

type SendOptions = {
  showUserMessage?: boolean;
};

export function ChatWorkspace() {
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const chatRef = useRef<HTMLDivElement | null>(null);
  const transactionsRef = useRef(transactions);

  const confirmedCount = useMemo(
    () => transactions.filter((transaction) => transaction.status !== "discarded").length,
    [transactions],
  );

  useEffect(() => {
    transactionsRef.current = transactions;
  }, [transactions]);

  useEffect(() => {
    try {
      const storedMessages = JSON.parse(localStorage.getItem(storageKeys.messages) || "null") as
        | ChatMessage[]
        | null;
      const storedTransactions = JSON.parse(
        localStorage.getItem(storageKeys.transactions) || "[]",
      ) as Transaction[];
      if (storedMessages?.length) setMessages(storedMessages);
      if (storedTransactions?.length) setTransactions(storedTransactions);
    } catch {
      setMessages([welcomeMessage]);
      setTransactions([]);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(storageKeys.messages, JSON.stringify(messages.slice(-80)));
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(storageKeys.transactions, JSON.stringify(transactions));
  }, [transactions]);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  });

  const push = (message: ChatMessage) => {
    setMessages((current) => [...current, message]);
  };

  const sendToAssistant = async (text: string, options: SendOptions = {}) => {
    const { showUserMessage = true } = options;

    if (showUserMessage) {
      push({
        id: `u-${Date.now()}`,
        role: "user",
        type: "text",
        content: text,
        timestamp: new Date().toISOString(),
      });
    }

    setLoading(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });

      const body = (await response.json()) as ChatApiResponse & {
        error?: { message?: string };
      };

      if (!response.ok) {
        throw new Error(body.error?.message || "Could not reach the assistant.");
      }

      const timestamp = new Date().toISOString();
      const assistantMessages = mapApiMessagesToChat(
        body.messages,
        transactionsRef.current,
        timestamp,
      );

      for (const message of assistantMessages) {
        push(message);
      }
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Please try again.";
      push({
        id: `err-${Date.now()}`,
        role: "assistant",
        type: "error",
        content: `Sorry, I had trouble with that. ${detail}`,
        timestamp: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (text: string) => {
    await sendToAssistant(text);
  };

  const handleConfirm = async (messageId: string, transaction: Transaction) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId ? { ...message, txStatus: "confirmed" } : message,
      ),
    );

    const parts = [
      "yes, confirm this transaction",
      `$${Number(transaction.amount).toFixed(2)}`,
      transaction.category,
    ];
    if (transaction.description) parts.push(transaction.description);
    parts.push(transaction.date || todayISO());

    await sendToAssistant(parts.join(", "), { showUserMessage: false });

    setTransactions((current) => {
      const exists = current.some((item) => item.id === transaction.id);
      if (exists) {
        return current.map((item) =>
          item.id === transaction.id
            ? {
                ...transaction,
                status: "confirmed",
                confirmedAt: new Date().toISOString(),
              }
            : item,
        );
      }
      return [
        ...current,
        {
          ...transaction,
          status: "confirmed",
          confirmedAt: new Date().toISOString(),
        },
      ];
    });
  };

  const handleCancel = async (messageId: string) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId ? { ...message, txStatus: "discarded" } : message,
      ),
    );
    await sendToAssistant("discard that transaction", { showUserMessage: false });
  };

  const handleReset = () => {
    if (!window.confirm("Clear all messages and transactions? This cannot be undone.")) return;
    setMessages([welcomeMessage]);
    setTransactions([]);
    localStorage.removeItem(storageKeys.messages);
    localStorage.removeItem(storageKeys.transactions);
  };

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">FG</div>
          <div>
            <div className="brand-title">Finguard</div>
            <div className="brand-subtitle">AI Financial Assistant</div>
          </div>
        </div>
        <div className="header-actions">
          {confirmedCount > 0 && <span className="tx-count">{confirmedCount} tx</span>}
          <button
            className={`button header-button ${sidebarOpen ? "button-primary" : "button-ghost"}`}
            onClick={() => setSidebarOpen((current) => !current)}
          >
            {sidebarOpen ? "Hide Overview" : "Overview"}
          </button>
          <button className="button button-ghost header-button" onClick={handleReset}>
            Reset
          </button>
        </div>
      </header>

      <main className="workspace">
        <section className="chat-pane">
          <div ref={chatRef} className="chat-scroll">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
              />
            ))}
            {loading && <TypingIndicator />}
          </div>
          <InputBar disabled={loading} onSend={handleSend} />
        </section>
        {sidebarOpen && (
          <DashboardPanel transactions={transactions} onClose={() => setSidebarOpen(false)} />
        )}
      </main>
    </div>
  );
}
