import type { ChatMessage } from "@/features/chat/types";
import type { Transaction } from "@/features/transactions/types";
import { categoryDisplay } from "@/lib/categories";
import { clearChatMessages, loadChatMessages, saveChatMessages } from "./chat-storage";

type ApiTransaction = {
  id: string;
  type: Transaction["type"];
  amount: number;
  category: string;
  description: string | null;
  transaction_date: string;
  status: Transaction["status"];
  updated_at?: string;
};

function mapApiTransaction(row: ApiTransaction): Transaction {
  return {
    id: row.id,
    type: row.type,
    amount: row.amount,
    category: categoryDisplay(row.category),
    description: row.description,
    date: row.transaction_date,
    status: row.status,
    confirmedAt: row.status === "confirmed" ? row.updated_at : undefined,
  };
}

function parseActionsError(status: number, text: string): string {
  try {
    const body = JSON.parse(text) as { error?: { message?: string; code?: string } };
    if (body.error?.message) return body.error.message;
    if (body.error?.code === "ACTIONS_UNAVAILABLE") {
      return "Action server is not running. From the project root, run: make dev";
    }
  } catch {
    // not JSON
  }
  return text || `Request failed: ${status}`;
}

async function actionsFetch(path: string, init?: RequestInit) {
  const response = await fetch(`/api${path}`, init);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(parseActionsError(response.status, text));
  }
  return response;
}

export async function fetchUserTransactions(): Promise<Transaction[]> {
  const response = await actionsFetch("/data/transactions");
  const data = (await response.json()) as ApiTransaction[];
  return data.map(mapApiTransaction);
}

export async function fetchChatMessages(): Promise<ChatMessage[]> {
  return loadChatMessages();
}

export async function persistChatMessage(
  message: ChatMessage,
  _userId: string,
): Promise<string | null> {
  if (message.id === "welcome") return null;
  const stored = loadChatMessages();
  const without = stored.filter((item) => item.id !== message.id);
  saveChatMessages([...without, message]);
  return message.id;
}

export async function updateChatMessageTxStatus(
  messageId: string,
  txStatus: "confirmed" | "discarded",
): Promise<void> {
  const stored = loadChatMessages();
  saveChatMessages(
    stored.map((message) => (message.id === messageId ? { ...message, txStatus } : message)),
  );
}

export async function clearChatHistory(): Promise<void> {
  clearChatMessages();
}

export async function clearAllTransactions(): Promise<void> {
  await actionsFetch("/data/transactions", { method: "DELETE" });
}

export async function clearUserFinancialData(): Promise<void> {
  await clearChatHistory();
  await clearAllTransactions();
}
