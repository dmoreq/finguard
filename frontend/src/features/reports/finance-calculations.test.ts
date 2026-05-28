import type { Transaction } from "@/features/transactions/types";
import { describe, expect, it } from "vitest";
import { computeDashboardData, computeReportData } from "./finance-calculations";

const NOW = new Date("2026-05-15T12:00:00");

function tx(partial: Partial<Transaction> & Pick<Transaction, "type" | "amount">): Transaction {
  return {
    id: partial.id ?? "t1",
    type: partial.type,
    amount: partial.amount,
    category: partial.category ?? "Food",
    description: partial.description ?? null,
    date: partial.date ?? "2026-05-10",
    status: partial.status ?? "confirmed",
  };
}

describe("computeDashboardData", () => {
  it("returns zeros for empty transactions", () => {
    const data = computeDashboardData([], NOW);
    expect(data.totalIncome).toBe(0);
    expect(data.totalExpenses).toBe(0);
    expect(data.net).toBe(0);
    expect(data.savingsRate).toBeNull();
    expect(data.pendingCount).toBe(0);
  });

  it("computes income-only savings rate at 100%", () => {
    const data = computeDashboardData(
      [tx({ type: "income", amount: 500, category: "Salary", date: "2026-05-08" })],
      NOW,
    );
    expect(data.totalIncome).toBe(500);
    expect(data.net).toBe(500);
    expect(data.savingsRate).toBe(100);
  });

  it("computes expense-only negative net", () => {
    const data = computeDashboardData(
      [tx({ type: "expense", amount: 40, date: "2026-05-12" })],
      NOW,
    );
    expect(data.totalExpenses).toBe(40);
    expect(data.net).toBe(-40);
    expect(data.savingsRate).toBeNull();
  });

  it("excludes pending from month expense totals but counts pendingCount", () => {
    const data = computeDashboardData(
      [
        tx({ type: "pending", amount: 99, date: "2026-05-14" }),
        tx({ type: "expense", amount: 10, date: "2026-05-14" }),
      ],
      NOW,
    );
    expect(data.totalExpenses).toBe(10);
    expect(data.pendingCount).toBe(1);
    expect(data.pendingTotal).toBe(99);
  });

  it("excludes invalid-date rows from thisMonth totals", () => {
    const data = computeDashboardData(
      [tx({ type: "expense", amount: 7, date: "not-a-date" })],
      NOW,
    );
    expect(data.txCount).toBe(0);
    expect(data.totalExpenses).toBe(0);
    expect(data.recordedTransactions).toHaveLength(1);
  });

  it("projects spend from daily average through month end", () => {
    const data = computeDashboardData(
      [tx({ type: "expense", amount: 150, date: "2026-05-15" })],
      NOW,
    );
    expect(data.dailySpend).toBe(10);
    expect(data.projectedSpend).toBe(310);
    expect(data.daysLeft).toBe(16);
  });
});

describe("computeReportData", () => {
  it("returns report subset of dashboard data", () => {
    const transactions = [
      tx({ type: "income", amount: 100, date: "2026-05-01" }),
      tx({ type: "expense", amount: 30, date: "2026-05-02" }),
    ];
    const report = computeReportData(transactions, NOW);
    expect(report.totalIncome).toBe(100);
    expect(report.totalExpenses).toBe(30);
    expect(report.net).toBe(70);
    expect(report.monthLabel).toContain("May");
  });
});
