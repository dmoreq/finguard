import type { Transaction } from "@/features/transactions/types";
import type { ChatApiMessage } from "@/server/chat/schemas";
import { describe, expect, it } from "vitest";
import { mapApiMessagesToChat } from "./map-api-messages";

const transactions: Transaction[] = [
  {
    id: "tx-1",
    type: "expense",
    amount: 20,
    category: "Food",
    description: null,
    date: "2026-05-10",
    status: "confirmed",
  },
];

describe("mapApiMessagesToChat", () => {
  it("maps transaction API message with pending_confirmation status", () => {
    const api: ChatApiMessage[] = [
      {
        type: "transaction",
        content: "Please confirm",
        transaction: {
          id: "tx-new",
          type: "expense",
          amount: 12,
          category: "Coffee",
          description: null,
          date: "2026-05-15",
          status: "pending_confirmation",
        },
      },
    ];
    const [msg] = mapApiMessagesToChat(api, transactions, "2026-05-15T00:00:00Z");
    expect(msg.type).toBe("transaction");
    if (msg.type === "transaction") {
      expect(msg.txStatus).toBe("pending_confirmation");
      expect(msg.transaction.id).toBe("tx-new");
    }
  });

  it("maps report with provided reportData", () => {
    const api: ChatApiMessage[] = [
      {
        type: "report",
        content: "Summary",
        reportData: {
          totalIncome: 1,
          totalExpenses: 2,
          net: -1,
          savingsRate: null,
          topCategory: null,
          topCategoryAmt: 0,
          dailySpend: 0,
          pendingTotal: 0,
          pendingCount: 0,
          monthLabel: "May 2026",
          txCount: 0,
        },
      },
    ];
    const [msg] = mapApiMessagesToChat(api, transactions, "ts");
    expect(msg.type).toBe("report");
    if (msg.type === "report") {
      expect(msg.reportData?.net).toBe(-1);
    }
  });

  it("falls back to computeReportData when report has no reportData", () => {
    const api: ChatApiMessage[] = [{ type: "report", content: "Summary" }];
    const [msg] = mapApiMessagesToChat(api, transactions, "ts");
    if (msg.type === "report") {
      expect(msg.reportData?.totalExpenses).toBe(20);
    }
  });

  it("maps error type", () => {
    const api: ChatApiMessage[] = [{ type: "error", content: "Oops" }];
    const [msg] = mapApiMessagesToChat(api, [], "ts");
    expect(msg.type).toBe("error");
    expect(msg.content).toBe("Oops");
  });

  it("maps plain text", () => {
    const api: ChatApiMessage[] = [{ type: "text", content: "Hello" }];
    const [msg] = mapApiMessagesToChat(api, [], "ts");
    expect(msg.type).toBe("text");
    expect(msg.role).toBe("assistant");
  });
});
