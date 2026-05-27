import { computeReportData } from "@/features/reports/finance-calculations";
import type { Transaction } from "@/features/transactions/types";
import type { ChatApiMessage } from "@/server/chat/schemas";
import type { ChatMessage } from "./types";

export function mapApiMessagesToChat(
  apiMessages: ChatApiMessage[],
  transactions: Transaction[],
  timestamp: string,
): ChatMessage[] {
  return apiMessages.map((item, index) => {
    const id = `a-${Date.now()}-${index}`;

    if (item.type === "transaction") {
      const transaction: Transaction = {
        id: item.transaction.id,
        type: item.transaction.type,
        amount: item.transaction.amount,
        category: item.transaction.category,
        description: item.transaction.description,
        date: item.transaction.date,
        status: item.transaction.status,
      };
      return {
        id,
        role: "assistant",
        type: "transaction",
        content: item.content,
        transaction,
        txStatus: "pending_confirmation",
        timestamp,
      };
    }

    if (item.type === "report") {
      return {
        id,
        role: "assistant",
        type: "report",
        content: item.content,
        reportData: item.reportData ?? computeReportData(transactions),
        timestamp,
      };
    }

    if (item.type === "error") {
      return {
        id,
        role: "assistant",
        type: "error",
        content: item.content,
        timestamp,
      };
    }

    return {
      id,
      role: "assistant",
      type: "text",
      content: item.content,
      timestamp,
    };
  });
}
