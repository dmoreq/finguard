"use client";

import type { DateRangeKey } from "@/features/reports/finance-calculations";
import { rangeLabel } from "@/features/reports/finance-calculations";
import type { Transaction } from "@/features/transactions/types";
import { categoryDisplay } from "@/lib/categories";
import { formatPlainMoney } from "@/lib/format";
import { useMemo, useState } from "react";

type Props = {
  transactions: Transaction[];
  locale?: string;
  currency?: string;
  onEdit: (transaction: Transaction) => void;
  onDelete: (id: string) => void;
  onAdd: () => void;
};

export function TransactionListPanel({
  transactions,
  locale = "vi",
  currency = "VND",
  onEdit,
  onDelete,
  onAdd,
}: Props) {
  const [range, setRange] = useState<DateRangeKey>("this_month");
  const isVi = locale.startsWith("vi");
  const money = (value: number) =>
    currency === "VND" ? `${formatPlainMoney(value)}₫` : `$${formatPlainMoney(value)}`;

  const rows = useMemo(() => {
    const now = new Date();
    return transactions.filter((tx) => {
      if (tx.type === "pending") return false;
      const date = new Date(`${tx.date}T12:00:00`);
      if (Number.isNaN(date.getTime())) return true;
      if (range === "this_month") {
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
      }
      if (range === "last_month") {
        const m = now.getMonth() === 0 ? 11 : now.getMonth() - 1;
        const y = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();
        return date.getMonth() === m && date.getFullYear() === y;
      }
      const days = range === "last_7d" ? 7 : 30;
      const start = new Date(now);
      start.setDate(now.getDate() - days);
      return date >= start && date <= now;
    });
  }, [transactions, range]);

  return (
    <section className="tx-list-panel">
      <div className="tx-list-head">
        <h2>{isVi ? "Giao dịch" : "Transactions"}</h2>
        <button type="button" className="button button-primary" onClick={onAdd}>
          {isVi ? "+ Thêm" : "+ Add"}
        </button>
      </div>
      <div className="tabs" style={{ marginBottom: 8 }}>
        {(["this_month", "last_month", "last_7d", "last_30d"] as const).map((key) => (
          <button
            key={key}
            type="button"
            className={`tab ${range === key ? "active" : ""}`}
            onClick={() => setRange(key)}
          >
            {rangeLabel(key, locale)}
          </button>
        ))}
      </div>
      {rows.length === 0 ? (
        <p className="tx-list-empty">
          {isVi ? "Không có giao dịch trong kỳ này." : "No transactions in this period."}
        </p>
      ) : (
        <ul className="tx-list">
          {rows.map((tx) => (
            <li key={tx.id} className="tx-list-row">
              <div>
                <div className="tx-list-title">{categoryDisplay(tx.category, locale)}</div>
                <div className="tx-list-meta">
                  {tx.date} ·{" "}
                  {tx.type === "income" ? (isVi ? "Thu" : "Income") : isVi ? "Chi" : "Expense"}
                </div>
              </div>
              <div className="tx-list-actions">
                <span className={tx.type === "income" ? "tx-income" : "tx-expense"}>
                  {tx.type === "income" ? "+" : "-"}
                  {money(tx.amount)}
                </span>
                <button type="button" className="button button-ghost" onClick={() => onEdit(tx)}>
                  {isVi ? "Sửa" : "Edit"}
                </button>
                <button
                  type="button"
                  className="button button-ghost"
                  onClick={() => onDelete(tx.id)}
                >
                  {isVi ? "Xóa" : "Delete"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
