"use client";

import type { Transaction } from "@/features/transactions/types";
import { formatPlainMoney } from "@/lib/format";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { computeDashboardData } from "./finance-calculations";

const palette = [
  "oklch(0.56 0.17 22)",
  "oklch(0.52 0.18 165)",
  "oklch(0.65 0.18 45)",
  "oklch(0.60 0.18 270)",
  "oklch(0.63 0.18 305)",
  "oklch(0.58 0.16 200)",
  "oklch(0.55 0.16 240)",
  "oklch(0.60 0.18 90)",
];

type Props = {
  transactions: Transaction[];
  onClose: () => void;
};

export function DashboardPanel({ transactions, onClose }: Props) {
  const [tab, setTab] = useState<"overview" | "income" | "expenses">("overview");
  const data = useMemo(() => computeDashboardData(transactions), [transactions]);
  const netPositive = data.net >= 0;
  const incomeTransactions = data.thisMonth.filter((transaction) => transaction.type === "income");
  const expenseTransactions = data.thisMonth.filter(
    (transaction) => transaction.type === "expense",
  );

  return (
    <aside className="dashboard">
      <div className="dashboard-head">
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 10,
          }}
        >
          <div>
            <div
              style={{
                color: "oklch(0.12 0.015 255)",
                fontFamily: "Sora, sans-serif",
                fontSize: 13,
                fontWeight: 800,
              }}
            >
              Report
            </div>
            <div
              style={{ color: "var(--text-muted)", fontSize: 10, fontWeight: 600, marginTop: 1 }}
            >
              {data.monthLabel}
            </div>
          </div>
          <button
            className="button"
            onClick={onClose}
            title="Close overview"
            style={{
              alignItems: "center",
              background: "oklch(0.95 0.006 250)",
              border: 0,
              display: "flex",
              height: 26,
              justifyContent: "center",
              padding: 0,
              width: 26,
            }}
          >
            x
          </button>
        </div>
        <div className="tabs">
          {(["overview", "income", "expenses"] as const).map((name) => (
            <button
              key={name}
              className={`tab ${tab === name ? "active" : ""}`}
              onClick={() => setTab(name)}
            >
              {name.charAt(0).toUpperCase() + name.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {tab === "overview" && (
        <div className="side-content">
          <div
            className="hero-stat"
            style={{
              border: `1.5px solid ${netPositive ? "oklch(0.84 0.08 145)" : "oklch(0.86 0.07 22)"}`,
              background: netPositive
                ? "linear-gradient(135deg, oklch(0.94 0.06 145), oklch(0.97 0.03 165))"
                : "linear-gradient(135deg, oklch(0.95 0.04 22), oklch(0.97 0.02 35))",
            }}
          >
            <div className="stat-label" style={{ marginBottom: 4 }}>
              Net Balance
            </div>
            <div
              style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}
            >
              <div
                style={{
                  color: netPositive ? "oklch(0.34 0.15 145)" : "oklch(0.42 0.13 22)",
                  fontFamily: "Sora, sans-serif",
                  fontSize: 28,
                  fontWeight: 800,
                  lineHeight: 1,
                }}
              >
                {netPositive ? "+" : "-"}${formatPlainMoney(Math.abs(data.net))}
              </div>
              {data.savingsRate !== null && (
                <div
                  style={{
                    borderRadius: 20,
                    background: netPositive ? "oklch(0.36 0.14 145)" : "oklch(0.42 0.13 22)",
                    color: "#fff",
                    fontSize: 11,
                    fontWeight: 800,
                    padding: "4px 10px",
                  }}
                >
                  {data.savingsRate}% saved
                </div>
              )}
            </div>
          </div>

          <div className="stat-grid">
            <StatCard
              label="Income"
              value={`+$${data.totalIncome >= 1000 ? `${(data.totalIncome / 1000).toFixed(1)}k` : formatPlainMoney(data.totalIncome)}`}
              sub={`${incomeTransactions.length} transaction${incomeTransactions.length !== 1 ? "s" : ""}`}
              accent="oklch(0.36 0.14 145)"
            />
            <StatCard
              label="Expenses"
              value={`$${data.totalExpenses >= 1000 ? `${(data.totalExpenses / 1000).toFixed(1)}k` : formatPlainMoney(data.totalExpenses)}`}
              sub={`${expenseTransactions.length} transaction${expenseTransactions.length !== 1 ? "s" : ""}`}
              accent="oklch(0.42 0.13 22)"
            />
            <StatCard
              label="Daily Spend"
              value={data.dailySpend > 0 ? `$${data.dailySpend.toFixed(0)}/day` : "-"}
              sub={data.daysLeft > 0 ? `${data.daysLeft} days left` : "Last day"}
              accent="oklch(0.60 0.18 270)"
            />
            <StatCard
              label="Pending"
              value={data.pendingCount > 0 ? `$${formatPlainMoney(data.pendingTotal)}` : "-"}
              sub={`${data.pendingCount} item${data.pendingCount !== 1 ? "s" : ""}`}
              accent="oklch(0.50 0.13 72)"
            />
          </div>

          <SectionLabel>Income vs Expenses</SectionLabel>
          <div className="panel">
            {data.totalIncome === 0 && data.totalExpenses === 0 ? (
              <p
                style={{
                  color: "var(--text-muted)",
                  fontSize: 11.5,
                  fontStyle: "italic",
                  margin: 0,
                }}
              >
                No data for this month yet.
              </p>
            ) : (
              <>
                <BarRow
                  label="Income"
                  value={data.totalIncome}
                  total={Math.max(data.totalIncome, data.totalExpenses)}
                  color="oklch(0.46 0.16 145)"
                />
                <BarRow
                  label="Expenses"
                  value={data.totalExpenses}
                  total={Math.max(data.totalIncome, data.totalExpenses)}
                  color="oklch(0.56 0.17 22)"
                />
                {data.pendingTotal > 0 && (
                  <BarRow
                    label="Pending"
                    value={data.pendingTotal}
                    total={Math.max(data.totalIncome, data.totalExpenses)}
                    color="oklch(0.60 0.13 72)"
                    prefix="~"
                  />
                )}
              </>
            )}
          </div>

          <SectionLabel extra={`${data.recordedTransactions.length} total`}>
            Recent Activity
          </SectionLabel>
          {data.recent.length === 0 ? (
            <p
              style={{
                color: "var(--text-muted)",
                fontSize: 11.5,
                fontStyle: "italic",
                lineHeight: 1.6,
              }}
            >
              No transactions yet. Start chatting to record your finances.
            </p>
          ) : (
            data.recent.map((transaction) => (
              <ActivityRow key={transaction.id} transaction={transaction} />
            ))
          )}
        </div>
      )}

      {tab === "income" && (
        <div className="side-content">
          <Hero
            label={`Total Income / ${data.monthLabel}`}
            value={`+$${formatPlainMoney(data.totalIncome)}`}
            color="oklch(0.34 0.15 145)"
            bg="linear-gradient(135deg, oklch(0.94 0.06 145), oklch(0.97 0.04 165))"
          />
          <SectionLabel>Income Sources</SectionLabel>
          <div className="panel">
            {data.incomeCategories.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 11.5, margin: 0 }}>
                No income recorded this month.
              </p>
            ) : (
              data.incomeCategories.map(([category, value], index) => (
                <BarRow
                  key={category}
                  label={category}
                  value={value}
                  total={data.totalIncome}
                  color={`oklch(${0.4 + index * 0.04} 0.16 145)`}
                />
              ))
            )}
          </div>
          <SectionLabel extra={`${incomeTransactions.length} entries`}>
            All Income Entries
          </SectionLabel>
          {incomeTransactions.map((transaction) => (
            <ActivityRow key={transaction.id} transaction={transaction} />
          ))}
        </div>
      )}

      {tab === "expenses" && (
        <div className="side-content">
          <Hero
            label={`Total Spent / ${data.monthLabel}`}
            value={`-$${formatPlainMoney(data.totalExpenses)}`}
            color="oklch(0.42 0.13 22)"
            bg="linear-gradient(135deg, oklch(0.95 0.04 22), oklch(0.97 0.025 35))"
          />
          <div className="stat-grid">
            <StatCard
              label="Avg Transaction"
              value={data.avgExpense > 0 ? `$${data.avgExpense.toFixed(2)}` : "-"}
              sub="per expense"
              accent="oklch(0.42 0.13 22)"
            />
            <StatCard
              label="Biggest Expense"
              value={data.maxExpense ? `$${formatPlainMoney(data.maxExpense.amount)}` : "-"}
              sub={data.maxExpense?.category ?? "-"}
              accent="oklch(0.56 0.17 22)"
            />
          </div>
          <SectionLabel>Category Detail</SectionLabel>
          <div className="panel">
            {data.expenseCategories.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 11.5, margin: 0 }}>
                No expenses recorded this month.
              </p>
            ) : (
              data.expenseCategories.map(([category, value], index) => (
                <BarRow
                  key={category}
                  label={category}
                  value={value}
                  total={data.totalExpenses}
                  color={palette[index % palette.length]}
                />
              ))
            )}
          </div>
          <SectionLabel extra={`${expenseTransactions.length} entries`}>
            All Expense Entries
          </SectionLabel>
          {expenseTransactions.map((transaction) => (
            <ActivityRow key={transaction.id} transaction={transaction} />
          ))}
        </div>
      )}
    </aside>
  );
}

function Hero({
  label,
  value,
  color,
  bg,
}: { label: string; value: string; color: string; bg: string }) {
  return (
    <div className="hero-stat" style={{ border: "1.5px solid var(--border)", background: bg }}>
      <div className="stat-label" style={{ marginBottom: 3 }}>
        {label}
      </div>
      <div
        style={{
          color,
          fontFamily: "Sora, sans-serif",
          fontSize: 28,
          fontWeight: 800,
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  sub,
  accent,
}: { label: string; value: string; sub: string; accent: string }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={{ color: accent }}>
        {value}
      </div>
      <div className="stat-sub">{sub}</div>
    </div>
  );
}

function SectionLabel({ children, extra }: { children: ReactNode; extra?: string }) {
  return (
    <div className="section-label">
      <span>{children}</span>
      {extra && (
        <span style={{ fontWeight: 700, letterSpacing: 0, textTransform: "none" }}>{extra}</span>
      )}
    </div>
  );
}

function BarRow({
  label,
  value,
  total,
  color,
  prefix = "",
}: { label: string; value: number; total: number; color: string; prefix?: string }) {
  const pct = total > 0 ? Math.max(2, (value / total) * 100) : 0;

  return (
    <div className="bar-row">
      <div className="bar-meta">
        <span style={{ color: "oklch(0.35 0.015 250)", fontSize: 11.5, fontWeight: 600 }}>
          {label}
        </span>
        <span style={{ color, fontSize: 11.5, fontWeight: 800 }}>
          {prefix}${formatPlainMoney(value)}
        </span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function ActivityRow({ transaction }: { transaction: Transaction }) {
  const color = transaction.type === "income" ? "oklch(0.36 0.14 145)" : "oklch(0.42 0.13 22)";

  return (
    <div className="activity-row">
      <div style={{ minWidth: 0, paddingRight: 8 }}>
        <div className="activity-title">{transaction.description || transaction.category}</div>
        <div className="activity-sub">
          {transaction.category} / {transaction.date}
        </div>
      </div>
      <span style={{ color, flexShrink: 0, fontSize: 12.5, fontWeight: 800 }}>
        {transaction.type === "income" ? "+" : "-"}${formatPlainMoney(transaction.amount)}
      </span>
    </div>
  );
}
