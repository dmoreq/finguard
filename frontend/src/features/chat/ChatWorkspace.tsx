"use client";

import { useSession } from "@/features/auth/useSession";
import { DashboardPanel } from "@/features/reports/DashboardPanel";
import { TransactionFormModal } from "@/features/transactions/TransactionFormModal";
import { TransactionListPanel } from "@/features/transactions/TransactionListPanel";
import type { Transaction } from "@/features/transactions/types";
import { categorySlug, inputPlaceholder, welcomeMessage } from "@/lib/categories";
import {
  type UserProfile,
  clearAllTransactions,
  clearChatHistory,
  createTransaction,
  deleteTransaction,
  fetchChatMessages,
  fetchUserProfile,
  fetchUserTransactions,
  patchTransaction,
  persistChatMessage,
  updateChatMessageTxStatus,
} from "@/lib/data/financial-data";
import { todayISO } from "@/lib/format";
import type { ChatApiResponse } from "@/server/chat/schemas";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { InputBar } from "./InputBar";
import { MessageBubble, TypingIndicator } from "./MessageBubble";
import { mapApiMessagesToChat } from "./map-api-messages";
import type { ChatMessage } from "./types";

const defaultWelcome = (locale: string): ChatMessage => ({
  id: "welcome",
  role: "assistant",
  type: "text",
  content: welcomeMessage(locale),
  timestamp: "initial",
});

type SendOptions = {
  showUserMessage?: boolean;
};

export function ChatWorkspace() {
  const { userId, loading: sessionLoading } = useSession();
  const [messages, setMessages] = useState<ChatMessage[]>([defaultWelcome("vi")]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [dataLoading, setDataLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [txPanelOpen, setTxPanelOpen] = useState(false);
  const [formTx, setFormTx] = useState<Transaction | null | undefined>(undefined);
  const [dataError, setDataError] = useState<string | null>(null);
  const [lastUserMessage, setLastUserMessage] = useState<string | null>(null);
  const chatRef = useRef<HTMLDivElement | null>(null);
  const transactionsRef = useRef(transactions);

  const confirmedCount = useMemo(
    () => transactions.filter((transaction) => transaction.status !== "discarded").length,
    [transactions],
  );

  useEffect(() => {
    transactionsRef.current = transactions;
  }, [transactions]);

  const locale = profile?.locale ?? "vi";
  const currency = profile?.currency ?? "VND";
  const isVi = locale.startsWith("vi");

  const refreshTransactions = useCallback(async () => {
    const rows = await fetchUserTransactions();
    setTransactions(rows);
  }, []);

  const loadInitialData = useCallback(async () => {
    if (!userId) return;
    setDataLoading(true);
    setDataError(null);
    try {
      const userProfile = await fetchUserProfile();
      setProfile(userProfile);
      const [storedMessages, storedTransactions] = await Promise.all([
        fetchChatMessages(),
        fetchUserTransactions(),
      ]);
      setTransactions(storedTransactions);
      const welcome = defaultWelcome(userProfile.locale);
      if (storedMessages.length > 0) {
        setMessages(storedMessages);
      } else {
        setMessages([welcome]);
      }
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Could not load your data.";
      setDataError(detail);
    } finally {
      setDataLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) return;
    void loadInitialData();
  }, [userId, loadInitialData]);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  });

  const push = async (message: ChatMessage) => {
    const localId = message.id;
    setMessages((current) => [...current, message]);
    if (!userId || message.id === "welcome") return;
    try {
      const dbId = await persistChatMessage(message, userId);
      if (dbId && dbId !== localId) {
        setMessages((current) =>
          current.map((item) => (item.id === localId ? { ...item, id: dbId } : item)),
        );
      }
    } catch {
      // Chat still works; persistence failure is non-fatal for the turn
    }
  };

  const sendToAssistant = async (text: string, options: SendOptions = {}) => {
    const { showUserMessage = true } = options;

    if (showUserMessage) {
      setLastUserMessage(text);
      await push({
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
        await push(message);
      }

      await refreshTransactions();
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Please try again.";
      const errId = `err-${Date.now()}`;
      await push({
        id: errId,
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

    if (messageId !== "welcome") {
      try {
        await updateChatMessageTxStatus(messageId, "confirmed");
      } catch {
        // Backend is source of truth for transaction status
      }
    }

    const parts = [
      isVi ? "xác nhận" : "yes, confirm this transaction",
      `$${Number(transaction.amount).toFixed(2)}`,
      categorySlug(transaction.category),
    ];
    if (transaction.description) parts.push(transaction.description);
    parts.push(transaction.date || todayISO());

    await sendToAssistant(parts.join(", "), { showUserMessage: false });
  };

  const handleCancel = async (messageId: string) => {
    setMessages((current) =>
      current.map((message) =>
        message.id === messageId ? { ...message, txStatus: "discarded" } : message,
      ),
    );

    if (messageId !== "welcome") {
      try {
        await updateChatMessageTxStatus(messageId, "discarded");
      } catch {
        // Non-fatal
      }
    }

    await sendToAssistant(isVi ? "hủy giao dịch" : "discard that transaction", {
      showUserMessage: false,
    });
  };

  const handleClearChat = async () => {
    if (!window.confirm("Clear chat history? Transactions stay in your records.")) return;
    try {
      await clearChatHistory();
      setMessages([defaultWelcome(locale)]);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Could not clear chat.");
    }
  };

  const handleClearTransactions = async () => {
    if (!window.confirm("Delete all transactions? This cannot be undone.")) return;
    try {
      await clearAllTransactions();
      setTransactions([]);
      await refreshTransactions();
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "Could not clear transactions.");
    }
  };

  if (sessionLoading || dataLoading) {
    return (
      <div className="app-root app-loading">
        <p>Loading your workspace…</p>
      </div>
    );
  }

  return (
    <div className="app-root">
      <header className="app-header">
        <div className="brand">
          <div className="brand-mark">FG</div>
          <div>
            <div className="brand-title">Finguard</div>
            <div className="brand-subtitle">
              {isVi ? "Trợ lý tài chính AI" : "AI Financial Assistant"}
            </div>
          </div>
        </div>
        <div className="header-actions">
          {confirmedCount > 0 && <span className="tx-count">{confirmedCount} tx</span>}
          <button
            className={`button header-button ${sidebarOpen ? "button-primary" : "button-ghost"}`}
            onClick={() => setSidebarOpen((current) => !current)}
          >
            {sidebarOpen ? (isVi ? "Ẩn báo cáo" : "Hide Overview") : isVi ? "Báo cáo" : "Overview"}
          </button>
          <button
            className={`button header-button ${txPanelOpen ? "button-primary" : "button-ghost"}`}
            onClick={() => setTxPanelOpen((current) => !current)}
          >
            {isVi ? "Giao dịch" : "Transactions"}
          </button>
          <button
            className="button button-ghost header-button"
            onClick={() => void handleClearChat()}
          >
            Clear chat
          </button>
          <button
            className="button button-ghost header-button"
            onClick={() => void handleClearTransactions()}
          >
            Clear txs
          </button>
          <a className="button button-ghost header-button" href="/settings">
            Settings
          </a>
          <a
            className="button button-ghost header-button"
            href="/api/transactions/export"
            download="finguard-transactions.csv"
          >
            Export CSV
          </a>
        </div>
      </header>

      {dataError && (
        <p className="data-error" role="alert">
          {dataError}{" "}
          <button
            type="button"
            className="button button-ghost"
            onClick={() => void loadInitialData()}
          >
            Retry
          </button>
        </p>
      )}

      <main className="workspace">
        <section className="chat-pane">
          <div ref={chatRef} className="chat-scroll">
            {messages.length <= 1 && confirmedCount === 0 && (
              <output className="empty-hint">
                {isVi
                  ? 'Chưa có giao dịch. Thử: "Chi tiêu 80k cà phê sáng nay."'
                  : 'No transactions yet. Try: "I spent $12 on coffee today."'}
              </output>
            )}
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                transactions={transactions}
                locale={locale}
                currency={currency}
                onConfirm={handleConfirm}
                onCancel={handleCancel}
                onRetry={
                  message.type === "error" && lastUserMessage
                    ? () => void sendToAssistant(lastUserMessage, { showUserMessage: false })
                    : undefined
                }
              />
            ))}
            {loading && <TypingIndicator />}
          </div>
          <InputBar disabled={loading} onSend={handleSend} placeholder={inputPlaceholder(locale)} />
        </section>
        {txPanelOpen && (
          <TransactionListPanel
            transactions={transactions}
            locale={locale}
            currency={currency}
            onAdd={() => setFormTx(null)}
            onEdit={(tx) => setFormTx(tx)}
            onDelete={async (id) => {
              if (!window.confirm(isVi ? "Xóa giao dịch này?" : "Delete this transaction?")) return;
              await deleteTransaction(id);
              await refreshTransactions();
            }}
          />
        )}
        {sidebarOpen && (
          <DashboardPanel
            transactions={transactions}
            locale={locale}
            currency={currency}
            onClose={() => setSidebarOpen(false)}
          />
        )}
      </main>
      {formTx !== undefined && (
        <TransactionFormModal
          locale={locale}
          initial={formTx ?? undefined}
          onClose={() => setFormTx(undefined)}
          onSave={async (payload) => {
            if (payload.id) {
              await patchTransaction(payload.id, {
                type: payload.type,
                amount: payload.amount,
                category: payload.category,
                description: payload.description,
                transaction_date: payload.transaction_date,
              });
            } else {
              await createTransaction(payload);
            }
            await refreshTransactions();
          }}
        />
      )}
    </div>
  );
}
