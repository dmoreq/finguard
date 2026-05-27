import type { ChatMessage } from "@/features/chat/types";
import type { ReportData } from "@/features/reports/finance-calculations";
import type {
  Transaction,
  TransactionStatus,
  TransactionType,
} from "@/features/transactions/types";
import { categoryDisplay } from "@/lib/categories";

export type TransactionRow = {
  id: string;
  user_id: string;
  type: TransactionType;
  amount: number | string;
  currency: string;
  category: string;
  description: string | null;
  transaction_date: string;
  status: TransactionStatus;
  source: string;
  ai_confidence: number | null;
  created_at: string;
  updated_at: string;
};

export type ChatMessageRow = {
  id: string;
  user_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  message_type: "text" | "transaction" | "report" | "error";
  transaction_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export function mapTransactionRow(row: TransactionRow): Transaction {
  return {
    id: row.id,
    type: row.type,
    amount: Number(row.amount),
    category: categoryDisplay(row.category),
    description: row.description,
    date: row.transaction_date,
    status: row.status,
    confirmedAt: row.status === "confirmed" ? row.updated_at : undefined,
    aiConfidence: row.ai_confidence ?? undefined,
  };
}

function readMetadataTransaction(metadata: Record<string, unknown> | null): Transaction | null {
  if (!metadata || typeof metadata.transaction !== "object" || !metadata.transaction) {
    return null;
  }
  const tx = metadata.transaction as Record<string, unknown>;
  if (typeof tx.id !== "string") return null;
  if (tx.type !== "income" && tx.type !== "expense" && tx.type !== "pending") return null;
  if (typeof tx.amount !== "number") return null;
  if (typeof tx.category !== "string") return null;
  if (typeof tx.date !== "string") return null;

  return {
    id: tx.id,
    type: tx.type,
    amount: tx.amount,
    category: tx.category,
    description: typeof tx.description === "string" ? tx.description : null,
    date: tx.date,
    status:
      tx.status === "pending_confirmation" || tx.status === "confirmed" || tx.status === "discarded"
        ? tx.status
        : "pending_confirmation",
    confirmedAt: typeof tx.confirmedAt === "string" ? tx.confirmedAt : undefined,
  };
}

function readMetadataReport(metadata: Record<string, unknown> | null): ReportData | undefined {
  if (!metadata || typeof metadata.reportData !== "object" || !metadata.reportData) {
    return undefined;
  }
  return metadata.reportData as ReportData;
}

export function mapChatMessageRow(row: ChatMessageRow): ChatMessage | null {
  if (row.role === "system") return null;

  const timestamp = row.created_at;
  const txStatus =
    typeof row.metadata?.txStatus === "string" ? (row.metadata.txStatus as string) : undefined;

  if (row.message_type === "transaction") {
    const transaction = readMetadataTransaction(row.metadata);
    if (!transaction) return null;
    return {
      id: row.id,
      role: row.role === "user" ? "user" : "assistant",
      type: "transaction",
      content: row.content,
      transaction,
      txStatus:
        txStatus === "confirmed" || txStatus === "discarded" ? txStatus : "pending_confirmation",
      timestamp,
    };
  }

  if (row.message_type === "report") {
    const reportData = readMetadataReport(row.metadata);
    if (!reportData) {
      return {
        id: row.id,
        role: "assistant",
        type: "text",
        content: row.content,
        timestamp,
      };
    }
    return {
      id: row.id,
      role: "assistant",
      type: "report",
      content: row.content,
      reportData,
      timestamp,
    };
  }

  if (row.message_type === "error") {
    return {
      id: row.id,
      role: "assistant",
      type: "error",
      content: row.content,
      timestamp,
    };
  }

  return {
    id: row.id,
    role: row.role === "user" ? "user" : "assistant",
    type: "text",
    content: row.content,
    timestamp,
  };
}

export function chatMessageToInsert(
  message: ChatMessage,
  userId: string,
): {
  user_id: string;
  role: "user" | "assistant";
  content: string;
  message_type: "text" | "transaction" | "report" | "error";
  transaction_id: string | null;
  metadata: Record<string, unknown>;
} {
  const role = message.role === "user" ? "user" : "assistant";

  if (message.type === "transaction" && message.transaction) {
    return {
      user_id: userId,
      role,
      content: message.content,
      message_type: "transaction",
      transaction_id: message.transaction.id,
      metadata: {
        transaction: message.transaction,
        txStatus: message.txStatus ?? "pending_confirmation",
      },
    };
  }

  if (message.type === "report") {
    return {
      user_id: userId,
      role: "assistant",
      content: message.content,
      message_type: "report",
      transaction_id: null,
      metadata: { reportData: message.reportData },
    };
  }

  return {
    user_id: userId,
    role,
    content: message.content,
    message_type: message.type === "error" ? "error" : "text",
    transaction_id: null,
    metadata: {},
  };
}
