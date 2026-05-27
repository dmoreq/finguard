import { describe, expect, it } from "vitest";
import { chatMessageToInsert, mapChatMessageRow, mapTransactionRow } from "./map-db-row";

describe("mapTransactionRow", () => {
  it("maps database row to UI transaction", () => {
    const result = mapTransactionRow({
      id: "tx-1",
      user_id: "user-1",
      type: "expense",
      amount: "45.50",
      currency: "USD",
      category: "food & dining",
      description: "lunch",
      transaction_date: "2026-05-27",
      status: "confirmed",
      source: "manual_chat",
      ai_confidence: 0.9,
      created_at: "2026-05-27T10:00:00Z",
      updated_at: "2026-05-27T10:05:00Z",
    });

    expect(result.id).toBe("tx-1");
    expect(result.amount).toBe(45.5);
    expect(result.category).toBe("Food & Dining");
    expect(result.confirmedAt).toBe("2026-05-27T10:05:00Z");
  });
});

describe("mapChatMessageRow", () => {
  it("maps transaction message from metadata", () => {
    const result = mapChatMessageRow({
      id: "msg-1",
      user_id: "user-1",
      role: "assistant",
      content: "Confirm this expense",
      message_type: "transaction",
      transaction_id: "tx-1",
      metadata: {
        transaction: {
          id: "tx-1",
          type: "expense",
          amount: 12,
          category: "Food",
          description: null,
          date: "2026-05-27",
          status: "pending_confirmation",
        },
        txStatus: "pending_confirmation",
      },
      created_at: "2026-05-27T12:00:00Z",
    });

    expect(result?.type).toBe("transaction");
    if (result?.type === "transaction") {
      expect(result.transaction?.amount).toBe(12);
    }
  });
});

describe("chatMessageToInsert", () => {
  it("builds insert payload for user text", () => {
    const row = chatMessageToInsert(
      {
        id: "local-1",
        role: "user",
        type: "text",
        content: "Hello",
        timestamp: "2026-05-27T12:00:00Z",
      },
      "user-1",
    );

    expect(row.user_id).toBe("user-1");
    expect(row.message_type).toBe("text");
    expect(row.metadata).toEqual({});
  });
});
