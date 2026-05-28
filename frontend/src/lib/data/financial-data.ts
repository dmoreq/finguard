import type { ChatMessage } from "@/features/chat/types";
import type { Transaction } from "@/features/transactions/types";
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
    category: row.category,
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

export type UserProfile = {
  display_name: string;
  currency: string;
  timezone: string;
  locale: string;
};

export async function fetchUserProfile(): Promise<UserProfile> {
  const response = await actionsFetch("/data/profile");
  const data = (await response.json()) as UserProfile;
  return {
    display_name: data.display_name ?? "Local user",
    currency: data.currency ?? "VND",
    timezone: data.timezone ?? "Asia/Ho_Chi_Minh",
    locale: data.locale ?? "vi",
  };
}

export async function createTransaction(payload: {
  type: "income" | "expense";
  amount: number;
  category: string;
  description?: string;
  transaction_date: string;
}): Promise<Transaction> {
  const response = await actionsFetch("/data/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const row = (await response.json()) as ApiTransaction;
  return mapApiTransaction(row);
}

export async function patchTransaction(
  id: string,
  payload: Partial<{
    type: "income" | "expense";
    amount: number;
    category: string;
    description: string;
    transaction_date: string;
  }>,
): Promise<Transaction> {
  const response = await actionsFetch(`/data/transactions/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const row = (await response.json()) as ApiTransaction;
  return mapApiTransaction(row);
}

export async function deleteTransaction(id: string): Promise<void> {
  await actionsFetch(`/data/transactions/${id}`, { method: "DELETE" });
}

export async function downloadBackup(): Promise<Blob> {
  const response = await actionsFetch("/data/backup");
  const data = await response.json();
  return new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
}

export async function restoreBackup(file: File): Promise<void> {
  const text = await file.text();
  const body = JSON.parse(text) as unknown;
  await actionsFetch("/data/backup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
