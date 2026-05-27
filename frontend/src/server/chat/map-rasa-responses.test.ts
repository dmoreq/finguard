import { describe, expect, it } from "vitest";
import { mapRasaWebhookToChatResponse } from "./map-rasa-responses";

describe("mapRasaWebhookToChatResponse", () => {
  it("maps transaction_pending custom payload", () => {
    const result = mapRasaWebhookToChatResponse([
      {
        custom: {
          type: "transaction_pending",
          text: "Got it — $45.00 for Groceries.",
          transaction: {
            id: "tx-1",
            type: "expense",
            amount: 45,
            category: "groceries",
            description: null,
            date: "2026-05-27",
          },
        },
      },
    ]);

    expect(result.messages).toHaveLength(1);
    expect(result.messages[0]?.type).toBe("transaction");
    if (result.messages[0]?.type === "transaction") {
      expect(result.messages[0].transaction.id).toBe("tx-1");
      expect(result.messages[0].transaction.amount).toBe(45);
    }
  });

  it("maps plain text responses", () => {
    const result = mapRasaWebhookToChatResponse([{ text: "Hello there" }]);
    expect(result.messages[0]).toEqual({ type: "text", content: "Hello there" });
  });

  it("maps spending_report to report type with structured data", () => {
    const result = mapRasaWebhookToChatResponse([
      {
        custom: {
          type: "spending_report",
          text: "**Spending for this month:**\nTotal: $100",
          data: {
            period: "this_month",
            total: 100,
            by_category: [{ category: "food", total: 100, count: 1 }],
          },
        },
      },
    ]);
    expect(result.messages[0]?.type).toBe("report");
    if (result.messages[0]?.type === "report") {
      expect(result.messages[0].reportData?.totalExpenses).toBe(100);
    }
  });

  it("returns default text when payload is empty", () => {
    const result = mapRasaWebhookToChatResponse([]);
    expect(result.messages[0]?.type).toBe("text");
    expect(result.messages[0]?.content).toContain("help");
  });
});
