export type ParseRequest = {
  message: string;
  today: string;
  transactions: Array<{
    id: string;
    type: "income" | "expense" | "pending";
    amount: number;
    category: string;
    description?: string | null;
    date: string;
  }>;
};

export type AiParseResult = {
  intent: "transaction" | "report" | "conversation";
  message: string;
  transaction: {
    id: string;
    type: "income" | "expense" | "pending";
    amount: number;
    category: string;
    description: string | null;
    date: string;
    status: "pending_confirmation";
    aiConfidence?: number;
  } | null;
};

export function parseRequest(value: unknown): ParseRequest {
  if (!isRecord(value)) throw new Error("Invalid request body");
  if (
    typeof value.message !== "string" ||
    value.message.trim().length === 0 ||
    value.message.length > 1000
  ) {
    throw new Error("Invalid message");
  }
  if (typeof value.today !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value.today)) {
    throw new Error("Invalid date");
  }

  return {
    message: value.message,
    today: value.today,
    transactions: Array.isArray(value.transactions)
      ? value.transactions.filter(isTransactionContext)
      : [],
  };
}

export function parseAiResult(value: unknown): AiParseResult {
  if (!isRecord(value)) throw new Error("Invalid AI result");
  if (
    value.intent !== "transaction" &&
    value.intent !== "report" &&
    value.intent !== "conversation"
  )
    throw new Error("Invalid AI intent");
  if (typeof value.message !== "string" || !value.message) throw new Error("Invalid AI message");

  if (value.transaction === null) {
    return { intent: value.intent, message: value.message, transaction: null };
  }

  if (!isRecord(value.transaction)) throw new Error("Invalid AI transaction");
  const transaction = value.transaction;
  if (
    transaction.type !== "income" &&
    transaction.type !== "expense" &&
    transaction.type !== "pending"
  )
    throw new Error("Invalid transaction type");
  if (typeof transaction.amount !== "number" || transaction.amount <= 0)
    throw new Error("Invalid transaction amount");
  if (typeof transaction.category !== "string" || !transaction.category)
    throw new Error("Invalid transaction category");
  if (typeof transaction.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(transaction.date))
    throw new Error("Invalid transaction date");

  return {
    intent: value.intent,
    message: value.message,
    transaction: {
      id:
        typeof transaction.id === "string" && transaction.id ? transaction.id : `tx-${Date.now()}`,
      type: transaction.type,
      amount: transaction.amount,
      category: transaction.category,
      description: typeof transaction.description === "string" ? transaction.description : null,
      date: transaction.date,
      status: "pending_confirmation",
      aiConfidence:
        typeof transaction.aiConfidence === "number"
          ? Math.max(0, Math.min(1, transaction.aiConfidence))
          : undefined,
    },
  };
}

function isTransactionContext(value: unknown): value is ParseRequest["transactions"][number] {
  return (
    isRecord(value) &&
    typeof value.id === "string" &&
    (value.type === "income" || value.type === "expense" || value.type === "pending") &&
    typeof value.amount === "number" &&
    typeof value.category === "string" &&
    typeof value.date === "string"
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
