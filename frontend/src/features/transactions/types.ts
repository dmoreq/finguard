export type TransactionType = "income" | "expense" | "pending";
export type TransactionStatus = "pending_confirmation" | "confirmed" | "discarded";

export type Transaction = {
  id: string;
  type: TransactionType;
  amount: number;
  category: string;
  description?: string | null;
  date: string;
  status?: TransactionStatus;
  confirmedAt?: string;
  aiConfidence?: number;
};

export const categories: Record<TransactionType, string[]> = {
  income: ["Salary", "Freelance", "Investment Returns", "Gift", "Refund", "Other Income"],
  expense: [
    "Food & Dining",
    "Transportation",
    "Housing & Rent",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Education",
    "Savings",
    "Other",
  ],
  pending: [
    "Food & Dining",
    "Transportation",
    "Housing & Rent",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Education",
    "Savings",
    "Other",
  ],
};

export const transactionConfig = {
  income: {
    bg: "oklch(0.96 0.04 145)",
    accent: "oklch(0.50 0.18 145)",
    dark: "oklch(0.34 0.15 145)",
    badge: "Income",
    sign: "+",
  },
  expense: {
    bg: "oklch(0.97 0.03 22)",
    accent: "oklch(0.56 0.17 22)",
    dark: "oklch(0.42 0.13 22)",
    badge: "Expense",
    sign: "-",
  },
  pending: {
    bg: "oklch(0.97 0.04 72)",
    accent: "oklch(0.68 0.15 72)",
    dark: "oklch(0.50 0.13 72)",
    badge: "Pending",
    sign: "~",
  },
} as const;
