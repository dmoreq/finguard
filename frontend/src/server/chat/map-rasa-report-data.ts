import type { ReportData } from "@/features/reports/finance-calculations";
import { categoryDisplay } from "@/lib/categories";

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function readNumber(value: unknown): number | null {
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

export function reportDataFromBalancePayload(data: unknown): ReportData | null {
  if (!isRecord(data)) return null;

  const income = readNumber(data.income);
  const expenses = readNumber(data.expenses);
  const net = readNumber(data.net);
  if (income === null || expenses === null || net === null) return null;

  const period = typeof data.period === "string" ? data.period : "this_month";
  const monthLabel = period.replaceAll("_", " ");

  const savingsRate = income > 0 ? Math.round((Math.max(0, net) / income) * 100) : null;

  return {
    totalIncome: income,
    totalExpenses: expenses,
    net,
    savingsRate,
    topCategory: null,
    topCategoryAmt: 0,
    dailySpend: 0,
    pendingTotal: 0,
    pendingCount: 0,
    monthLabel,
    txCount: 0,
  };
}

export function reportDataFromSpendingPayload(data: unknown): ReportData | null {
  if (!isRecord(data)) return null;

  const total = readNumber(data.total);
  if (total === null) return null;

  const period = typeof data.period === "string" ? data.period : "this_month";
  const byCategory = Array.isArray(data.by_category) ? data.by_category : [];
  let topCategory: string | null = null;
  let topCategoryAmt = 0;

  for (const item of byCategory) {
    if (!isRecord(item)) continue;
    const catTotal = readNumber(item.total);
    if (catTotal === null) continue;
    if (catTotal > topCategoryAmt) {
      topCategoryAmt = catTotal;
      topCategory = typeof item.category === "string" ? categoryDisplay(item.category) : null;
    }
  }

  return {
    totalIncome: 0,
    totalExpenses: total,
    net: -total,
    savingsRate: null,
    topCategory,
    topCategoryAmt,
    dailySpend: 0,
    pendingTotal: 0,
    pendingCount: 0,
    monthLabel: period.replaceAll("_", " "),
    txCount: byCategory.length,
  };
}
