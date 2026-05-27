import {
  reportDataFromBalancePayload,
  reportDataFromSpendingPayload,
} from "./map-rasa-report-data";
import type { ChatApiMessage, ChatApiResponse, RasaWebhookPayload } from "./schemas";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function readCustomPayload(item: RasaWebhookPayload): Record<string, unknown> | null {
  const raw = item.custom ?? item.json_message;
  return isRecord(raw) ? raw : null;
}

function mapTransactionPending(
  payload: Record<string, unknown>,
  fallbackText: string,
): ChatApiMessage | null {
  const tx = payload.transaction;
  if (!isRecord(tx)) return null;

  const type = tx.type;
  if (type !== "income" && type !== "expense" && type !== "pending") return null;
  if (typeof tx.amount !== "number" || tx.amount <= 0) return null;
  if (typeof tx.category !== "string" || !tx.category) return null;

  const date =
    typeof tx.date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(tx.date)
      ? tx.date
      : new Date().toISOString().slice(0, 10);

  const id = typeof tx.id === "string" && tx.id ? tx.id : `tx-${Date.now()}`;

  const text = typeof payload.text === "string" && payload.text ? payload.text : fallbackText;

  return {
    type: "transaction",
    content: text,
    transaction: {
      id,
      type,
      amount: tx.amount,
      category: tx.category,
      description:
        typeof tx.description === "string" ? tx.description : tx.description === null ? null : null,
      date,
      status: "pending_confirmation",
    },
  };
}

function mapReportMessage(custom: Record<string, unknown>, text: string): ChatApiMessage | null {
  const customType = custom.type;
  const reportText = typeof custom.text === "string" && custom.text ? custom.text : text;
  if (!reportText) return null;

  const data = custom.data;
  const reportData =
    customType === "balance"
      ? reportDataFromBalancePayload(data)
      : customType === "spending_report"
        ? reportDataFromSpendingPayload(data)
        : null;

  return {
    type: "report",
    content: reportText,
    ...(reportData ? { reportData } : {}),
  };
}

export function mapRasaWebhookToChatResponse(items: RasaWebhookPayload[]): ChatApiResponse {
  const messages: ChatApiMessage[] = [];

  for (const item of items) {
    const custom = readCustomPayload(item);
    const text = typeof item.text === "string" ? item.text : "";

    if (custom) {
      const customType = custom.type;
      if (customType === "transaction_pending") {
        const mapped = mapTransactionPending(
          custom,
          text || "I detected a transaction. Confirm the details below.",
        );
        if (mapped) {
          messages.push(mapped);
          continue;
        }
      }
      if (customType === "spending_report" || customType === "balance") {
        const mapped = mapReportMessage(custom, text);
        if (mapped) {
          messages.push(mapped);
          continue;
        }
      }
      if (customType === "transaction_list") {
        const listText = typeof custom.text === "string" && custom.text ? custom.text : text;
        if (listText) {
          messages.push({ type: "text", content: listText });
          continue;
        }
      }
    }

    if (text) {
      messages.push({ type: "text", content: text });
    }
  }

  if (messages.length === 0) {
    messages.push({
      type: "text",
      content: "I'm here to help with your finances.",
    });
  }

  return { messages };
}
