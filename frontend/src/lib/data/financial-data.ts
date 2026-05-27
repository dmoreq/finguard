import type { ChatMessage } from "@/features/chat/types";
import type { Transaction } from "@/features/transactions/types";
import { createClient } from "@/lib/supabase/client";
import {
  type ChatMessageRow,
  type TransactionRow,
  chatMessageToInsert,
  mapChatMessageRow,
  mapTransactionRow,
} from "./map-db-row";

const ALL_ROWS = "00000000-0000-0000-0000-000000000000";

export async function fetchUserTransactions(): Promise<Transaction[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("transactions")
    .select("*")
    .neq("status", "discarded")
    .order("transaction_date", { ascending: false });

  if (error) throw new Error(error.message);
  return ((data ?? []) as TransactionRow[]).map(mapTransactionRow);
}

export async function fetchChatMessages(limit = 80): Promise<ChatMessage[]> {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("chat_messages")
    .select("*")
    .order("created_at", { ascending: true })
    .limit(limit);

  if (error) throw new Error(error.message);

  const messages: ChatMessage[] = [];
  for (const row of (data ?? []) as ChatMessageRow[]) {
    const mapped = mapChatMessageRow(row);
    if (mapped) messages.push(mapped);
  }
  return messages;
}

export async function persistChatMessage(message: ChatMessage, userId: string): Promise<void> {
  if (message.id === "welcome") return;

  const supabase = createClient();
  const { error } = await supabase
    .from("chat_messages")
    .insert(chatMessageToInsert(message, userId));

  if (error) throw new Error(error.message);
}

export async function updateChatMessageTxStatus(
  messageId: string,
  txStatus: "confirmed" | "discarded",
): Promise<void> {
  const supabase = createClient();
  const { data: row, error: fetchError } = await supabase
    .from("chat_messages")
    .select("metadata")
    .eq("id", messageId)
    .maybeSingle();

  if (fetchError) throw new Error(fetchError.message);
  if (!row) return;

  const metadata = (row.metadata as Record<string, unknown> | null) ?? {};
  const { error } = await supabase
    .from("chat_messages")
    .update({ metadata: { ...metadata, txStatus } })
    .eq("id", messageId);

  if (error) throw new Error(error.message);
}

export async function clearUserFinancialData(): Promise<void> {
  const supabase = createClient();

  const { error: txError } = await supabase.from("transactions").delete().neq("id", ALL_ROWS);

  if (txError) throw new Error(txError.message);

  const { error: msgError } = await supabase.from("chat_messages").delete().neq("id", ALL_ROWS);

  if (msgError) throw new Error(msgError.message);
}
