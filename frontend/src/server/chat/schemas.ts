export type ChatRequest = {
  message: string;
};

export type ChatApiMessage =
  | {
      type: "text";
      content: string;
    }
  | {
      type: "transaction";
      content: string;
      transaction: {
        id: string;
        type: "income" | "expense" | "pending";
        amount: number;
        category: string;
        description: string | null;
        date: string;
        status: "pending_confirmation";
      };
    }
  | {
      type: "report";
      content: string;
      reportData?: import("@/features/reports/finance-calculations").ReportData;
    }
  | {
      type: "error";
      content: string;
    };

export type ChatApiResponse = {
  messages: ChatApiMessage[];
};

export function parseChatRequest(value: unknown): ChatRequest {
  if (!isRecord(value)) throw new Error("Invalid request body");
  if (
    typeof value.message !== "string" ||
    value.message.trim().length === 0 ||
    value.message.length > 2000
  ) {
    throw new Error("Invalid message");
  }
  return { message: value.message.trim() };
}

export type RasaWebhookPayload = {
  recipient_id?: string;
  text?: string;
  custom?: unknown;
  json_message?: unknown;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
