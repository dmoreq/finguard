import type { Transaction } from "@/features/transactions/types";

export type DateRangeKey = "this_month" | "last_month" | "last_7d" | "last_30d";

export type ReportData = {
  totalIncome: number;
  totalExpenses: number;
  net: number;
  savingsRate: number | null;
  topCategory: string | null;
  topCategoryAmt: number;
  dailySpend: number;
  pendingTotal: number;
  pendingCount: number;
  monthLabel: string;
  txCount: number;
  priorExpenses: number | null;
  expenseTrendPct: number | null;
};

export type DashboardData = ReportData & {
  filtered: Transaction[];
  recordedTransactions: Transaction[];
  expenseCategories: Array<[string, number]>;
  incomeCategories: Array<[string, number]>;
  recent: Transaction[];
  avgExpense: number;
  maxExpense: Transaction | null;
  daysLeft: number;
  projectedSpend: number;
};

const RANGE_LABELS_VI: Record<DateRangeKey, string> = {
  this_month: "Tháng này",
  last_month: "Tháng trước",
  last_7d: "7 ngày qua",
  last_30d: "30 ngày qua",
};

const RANGE_LABELS_EN: Record<DateRangeKey, string> = {
  this_month: "This month",
  last_month: "Last month",
  last_7d: "Last 7 days",
  last_30d: "Last 30 days",
};

export function rangeLabel(key: DateRangeKey, locale = "vi"): string {
  const labels = locale.startsWith("vi") ? RANGE_LABELS_VI : RANGE_LABELS_EN;
  return labels[key];
}

function inRange(dateStr: string, range: DateRangeKey, now: Date): boolean {
  const date = new Date(`${dateStr}T12:00:00`);
  if (Number.isNaN(date.getTime())) return true;

  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59);

  switch (range) {
    case "this_month":
      return date >= startOfMonth && date <= endOfMonth;
    case "last_month": {
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const end = new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59);
      return date >= start && date <= end;
    }
    case "last_7d": {
      const start = new Date(now);
      start.setDate(now.getDate() - 7);
      return date >= start && date <= now;
    }
    case "last_30d": {
      const start = new Date(now);
      start.setDate(now.getDate() - 30);
      return date >= start && date <= now;
    }
    default:
      return true;
  }
}

function priorRange(range: DateRangeKey): DateRangeKey {
  if (range === "this_month") return "last_month";
  return range;
}

export function computeDashboardData(
  transactions: Transaction[],
  now = new Date(),
  range: DateRangeKey = "this_month",
  locale = "vi",
): DashboardData {
  const monthLabel = rangeLabel(range, locale);
  const filtered = transactions.filter((transaction) => {
    if (transaction.type === "pending") return false;
    return inRange(transaction.date, range, now);
  });

  const priorFiltered = transactions.filter((transaction) => {
    if (transaction.type === "pending") return false;
    return inRange(transaction.date, priorRange(range), now);
  });

  const recordedTransactions = transactions.filter((transaction) => transaction.type !== "pending");
  const incomeTransactions = filtered.filter((transaction) => transaction.type === "income");
  const expenseTransactions = filtered.filter((transaction) => transaction.type === "expense");
  const priorExpenses = priorFiltered
    .filter((t) => t.type === "expense")
    .reduce((sum, t) => sum + (t.amount || 0), 0);
  const pendingItems = transactions.filter((transaction) => transaction.type === "pending");
  const totalIncome = incomeTransactions.reduce(
    (sum, transaction) => sum + (transaction.amount || 0),
    0,
  );
  const totalExpenses = expenseTransactions.reduce(
    (sum, transaction) => sum + (transaction.amount || 0),
    0,
  );
  const pendingTotal = pendingItems.reduce(
    (sum, transaction) => sum + (transaction.amount || 0),
    0,
  );
  const net = totalIncome - totalExpenses;
  const savingsRate = totalIncome > 0 ? Math.round((Math.max(0, net) / totalIncome) * 100) : null;
  const expenseCategories = aggregateCategories(expenseTransactions);
  const incomeCategories = aggregateCategories(incomeTransactions);
  const topCategory = expenseCategories[0] ?? null;
  const dayOfMonth = now.getDate();
  const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
  const dailySpend = dayOfMonth > 0 && totalExpenses > 0 ? totalExpenses / dayOfMonth : 0;
  const daysLeft = Math.max(0, daysInMonth - dayOfMonth);
  const projectedSpend = dailySpend * daysInMonth;
  const maxExpense =
    expenseTransactions.reduce<Transaction | null>((max, transaction) => {
      if (!max || transaction.amount > max.amount) return transaction;
      return max;
    }, null) ?? null;

  let expenseTrendPct: number | null = null;
  if (priorExpenses > 0) {
    expenseTrendPct = Math.round(((totalExpenses - priorExpenses) / priorExpenses) * 100);
  }

  return {
    totalIncome,
    totalExpenses,
    net,
    savingsRate,
    topCategory: topCategory?.[0] ?? null,
    topCategoryAmt: topCategory?.[1] ?? 0,
    dailySpend,
    pendingTotal,
    pendingCount: pendingItems.length,
    monthLabel,
    txCount: filtered.length,
    priorExpenses,
    expenseTrendPct,
    filtered,
    recordedTransactions,
    expenseCategories,
    incomeCategories,
    recent: [...recordedTransactions]
      .sort(
        (a, b) =>
          new Date(b.confirmedAt || b.date || 0).getTime() -
          new Date(a.confirmedAt || a.date || 0).getTime(),
      )
      .slice(0, 8),
    avgExpense: expenseTransactions.length > 0 ? totalExpenses / expenseTransactions.length : 0,
    maxExpense,
    daysLeft,
    projectedSpend,
  };
}

export function computeReportData(
  transactions: Transaction[],
  now = new Date(),
  range: DateRangeKey = "this_month",
  locale = "vi",
): ReportData {
  const data = computeDashboardData(transactions, now, range, locale);
  return {
    totalIncome: data.totalIncome,
    totalExpenses: data.totalExpenses,
    net: data.net,
    savingsRate: data.savingsRate,
    topCategory: data.topCategory,
    topCategoryAmt: data.topCategoryAmt,
    dailySpend: data.dailySpend,
    pendingTotal: data.pendingTotal,
    pendingCount: data.pendingCount,
    monthLabel: data.monthLabel,
    txCount: data.txCount,
    priorExpenses: data.priorExpenses,
    expenseTrendPct: data.expenseTrendPct,
  };
}

function aggregateCategories(transactions: Transaction[]) {
  const map = new Map<string, number>();
  for (const transaction of transactions) {
    map.set(transaction.category, (map.get(transaction.category) ?? 0) + (transaction.amount || 0));
  }
  return [...map.entries()].sort((a, b) => b[1] - a[1]);
}
