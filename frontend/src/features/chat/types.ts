import type { ReportData } from "@/features/reports/finance-calculations";
import type { Transaction } from "@/features/transactions/types";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  type: "text" | "transaction" | "report" | "error";
  content: string;
  transaction?: Transaction;
  reportData?: ReportData;
  txStatus?: "pending_confirmation" | "confirmed" | "discarded";
  timestamp: string;
};
