import { describe, expect, it } from "vitest";
import {
  reportDataFromBalancePayload,
  reportDataFromSpendingPayload,
} from "./map-rasa-report-data";

describe("reportDataFromBalancePayload", () => {
  it("maps balance data from Rasa", () => {
    const result = reportDataFromBalancePayload({
      period: "this_month",
      income: 3200,
      expenses: 450,
      net: 2750,
      currency: "USD",
    });
    expect(result?.totalIncome).toBe(3200);
    expect(result?.totalExpenses).toBe(450);
    expect(result?.net).toBe(2750);
    expect(result?.savingsRate).toBe(86);
  });

  it("returns null for invalid payload", () => {
    expect(reportDataFromBalancePayload({ income: "nope" })).toBeNull();
  });
});

describe("reportDataFromSpendingPayload", () => {
  it("maps spending breakdown", () => {
    const result = reportDataFromSpendingPayload({
      period: "this_month",
      total: 200,
      by_category: [
        { category: "food", total: 120, count: 2 },
        { category: "transport", total: 80, count: 1 },
      ],
    });
    expect(result?.totalExpenses).toBe(200);
    expect(result?.topCategory).toBe("Food");
    expect(result?.topCategoryAmt).toBe(120);
  });
});
