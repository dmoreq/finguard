import type { Transaction } from "@/features/transactions/types";

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
};

export type DashboardData = ReportData & {
  thisMonth: Transaction[];
  recordedTransactions: Transaction[];
  expenseCategories: Array<[string, number]>;
  incomeCategories: Array<[string, number]>;
  recent: Transaction[];
  avgExpense: number;
  maxExpense: Transaction | null;
  daysLeft: number;
  projectedSpend: number;
};

export function computeDashboardData(transactions: Transaction[], now = new Date()): DashboardData {
  const monthLabel = now.toLocaleDateString("en-US", { month: "long", year: "numeric" });
  const thisMonth = transactions.filter((transaction) => {
    if (transaction.type === "pending") return false;

    try {
      const date = new Date(`${transaction.date}T12:00:00`);
      return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
    } catch {
      return true;
    }
  });

  const recordedTransactions = transactions.filter((transaction) => transaction.type !== "pending");
  const incomeTransactions = thisMonth.filter((transaction) => transaction.type === "income");
  const expenseTransactions = thisMonth.filter((transaction) => transaction.type === "expense");
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
    txCount: thisMonth.length,
    thisMonth,
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

export function computeReportData(transactions: Transaction[], now = new Date()): ReportData {
  const data = computeDashboardData(transactions, now);

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
  };
}

function aggregateCategories(transactions: Transaction[]) {
  const map = new Map<string, number>();

  for (const transaction of transactions) {
    map.set(transaction.category, (map.get(transaction.category) ?? 0) + (transaction.amount || 0));
  }

  return [...map.entries()].sort((a, b) => b[1] - a[1]);
}
