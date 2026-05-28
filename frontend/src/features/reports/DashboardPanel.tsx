"use client";

import type { Transaction } from "@/features/transactions/types";
import { categoryDisplay } from "@/lib/categories";
import { formatPlainMoney } from "@/lib/format";
import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import { type DateRangeKey, computeDashboardData, rangeLabel } from "./finance-calculations";

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
  locale?: string;
  currency?: string;
  onClose: () => void;
};

export function DashboardPanel({ transactions, locale = "vi", currency = "VND", onClose }: Props) {
  const [tab, setTab] = useState<"overview" | "income" | "expenses">("overview");
  const [range, setRange] = useState<DateRangeKey>("this_month");
  const data = useMemo(
    () => computeDashboardData(transactions, new Date(), range, locale),
    [transactions, range, locale],
  );
  const netPositive = data.net >= 0;
  const isVi = locale.startsWith("vi");
  const money = (value: number, sign = "") =>
    currency === "VND"
      ? `${sign}${formatPlainMoney(value)}₫`
      : `${sign}$${formatPlainMoney(value)}`;
  const incomeTransactions = data.filtered.filter((transaction) => transaction.type === "income");
  const expenseTransactions = data.filtered.filter((transaction) => transaction.type === "expense");

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
              {isVi ? "Báo cáo" : "Report"}
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
        <div className="tabs" style={{ marginBottom: 8 }}>
          {(["this_month", "last_month", "last_7d", "last_30d"] as const).map((key) => (
            <button
              key={key}
              className={`tab ${range === key ? "active" : ""}`}
              onClick={() => setRange(key)}
              style={{ fontSize: 10 }}
            >
              {rangeLabel(key, locale)}
            </button>
          ))}
        </div>
        <div className="tabs">
          {(["overview", "income", "expenses"] as const).map((name) => (
            <button
              key={name}
              className={`tab ${tab === name ? "active" : ""}`}
              onClick={() => setTab(name)}
            >
              {isVi
                ? { overview: "Tổng quan", income: "Thu", expenses: "Chi" }[name]
                : name.charAt(0).toUpperCase() + name.slice(1)}
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
              {isVi ? "Số dư ròng" : "Net Balance"}
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
                {netPositive ? "+" : "-"}
                {money(Math.abs(data.net))}
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
                  {data.savingsRate}% {isVi ? "tiết kiệm" : "saved"}
                </div>
              )}
            </div>
            {data.expenseTrendPct !== null && (
              <div style={{ marginTop: 8, fontSize: 11, color: "var(--text-muted)" }}>
                {isVi ? "Chi tiêu so kỳ trước:" : "Expense vs prior:"}{" "}
                <strong>
                  {data.expenseTrendPct > 0 ? "+" : ""}
                  {data.expenseTrendPct}%
                </strong>
              </div>
            )}
          </div>

          <div className="stat-grid">
            <StatCard
              label={isVi ? "Thu" : "Income"}
              value={`+${money(data.totalIncome)}`}
              sub={`${incomeTransactions.length} ${isVi ? "giao dịch" : "transactions"}`}
              accent="oklch(0.36 0.14 145)"
            />
            <StatCard
              label={isVi ? "Chi" : "Expenses"}
              value={money(data.totalExpenses)}
              sub={`${expenseTransactions.length} ${isVi ? "giao dịch" : "transactions"}`}
              accent="oklch(0.42 0.13 22)"
            />
            <StatCard
              label={isVi ? "Chi/ngày" : "Daily Spend"}
              value={
                data.dailySpend > 0 ? `${money(data.dailySpend)}/${isVi ? "ngày" : "day"}` : "-"
              }
              sub={
                data.daysLeft > 0
                  ? `${data.daysLeft} ${isVi ? "ngày còn lại" : "days left"}`
                  : isVi
                    ? "Ngày cuối tháng"
                    : "Last day"
              }
              accent="oklch(0.60 0.18 270)"
            />
            <StatCard
              label={isVi ? "Chờ xác nhận" : "Pending"}
              value={data.pendingCount > 0 ? money(data.pendingTotal) : "-"}
              sub={`${data.pendingCount} ${isVi ? "mục" : "items"}`}
              accent="oklch(0.50 0.13 72)"
            />
          </div>

          <SectionLabel>{isVi ? "Thu vs Chi" : "Income vs Expenses"}</SectionLabel>
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
                {isVi ? "Chưa có dữ liệu trong kỳ này." : "No data for this period yet."}
              </p>
            ) : (
              <>
                <BarRow
                  label={isVi ? "Thu" : "Income"}
                  value={data.totalIncome}
                  total={Math.max(data.totalIncome, data.totalExpenses)}
                  color="oklch(0.46 0.16 145)"
                  format={money}
                />
                <BarRow
                  label={isVi ? "Chi" : "Expenses"}
                  value={data.totalExpenses}
                  total={Math.max(data.totalIncome, data.totalExpenses)}
                  color="oklch(0.56 0.17 22)"
                  format={money}
                />
              </>
            )}
          </div>

          <SectionLabel extra={`${data.recordedTransactions.length} ${isVi ? "tổng" : "total"}`}>
            {isVi ? "Hoạt động gần đây" : "Recent Activity"}
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
              {isVi
                ? "Chưa có giao dịch. Hãy chat để ghi chi tiêu."
                : "No transactions yet. Start chatting to record your finances."}
            </p>
          ) : (
            data.recent.map((transaction) => (
              <ActivityRow
                key={transaction.id}
                transaction={transaction}
                locale={locale}
                format={money}
              />
            ))
          )}
        </div>
      )}

      {tab === "income" && (
        <div className="side-content">
          <Hero
            label={`${isVi ? "Tổng thu" : "Total Income"} / ${data.monthLabel}`}
            value={`+${money(data.totalIncome)}`}
            color="oklch(0.34 0.15 145)"
            bg="linear-gradient(135deg, oklch(0.94 0.06 145), oklch(0.97 0.04 165))"
          />
          <SectionLabel>{isVi ? "Nguồn thu" : "Income Sources"}</SectionLabel>
          <div className="panel">
            {data.incomeCategories.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 11.5, margin: 0 }}>
                {isVi ? "Chưa có thu nhập." : "No income recorded."}
              </p>
            ) : (
              data.incomeCategories.map(([category, value], index) => (
                <BarRow
                  key={category}
                  label={categoryDisplay(category, locale)}
                  value={value}
                  total={data.totalIncome}
                  color={`oklch(${0.4 + index * 0.04} 0.16 145)`}
                  format={money}
                />
              ))
            )}
          </div>
        </div>
      )}

      {tab === "expenses" && (
        <div className="side-content">
          <Hero
            label={`${isVi ? "Tổng chi" : "Total Spent"} / ${data.monthLabel}`}
            value={`-${money(data.totalExpenses)}`}
            color="oklch(0.42 0.13 22)"
            bg="linear-gradient(135deg, oklch(0.95 0.04 22), oklch(0.97 0.025 35))"
          />
          <SectionLabel>{isVi ? "Theo danh mục" : "Category Detail"}</SectionLabel>
          <div className="panel">
            {data.expenseCategories.length === 0 ? (
              <p style={{ color: "var(--text-muted)", fontSize: 11.5, margin: 0 }}>
                {isVi ? "Chưa có chi tiêu." : "No expenses recorded."}
              </p>
            ) : (
              data.expenseCategories.map(([category, value], index) => (
                <BarRow
                  key={category}
                  label={categoryDisplay(category, locale)}
                  value={value}
                  total={data.totalExpenses}
                  color={palette[index % palette.length]}
                  format={money}
                />
              ))
            )}
          </div>
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
  format,
  prefix = "",
}: {
  label: string;
  value: number;
  total: number;
  color: string;
  format: (n: number, sign?: string) => string;
  prefix?: string;
}) {
  const pct = total > 0 ? Math.max(2, (value / total) * 100) : 0;
  return (
    <div className="bar-row">
      <div className="bar-meta">
        <span style={{ color: "oklch(0.35 0.015 250)", fontSize: 11.5, fontWeight: 600 }}>
          {label}
        </span>
        <span style={{ color, fontSize: 11.5, fontWeight: 800 }}>
          {prefix}
          {format(value)}
        </span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function ActivityRow({
  transaction,
  locale,
  format,
}: { transaction: Transaction; locale: string; format: (n: number, sign?: string) => string }) {
  const color = transaction.type === "income" ? "oklch(0.36 0.14 145)" : "oklch(0.42 0.13 22)";
  return (
    <div className="activity-row">
      <div style={{ minWidth: 0, paddingRight: 8 }}>
        <div className="activity-title">
          {transaction.description || categoryDisplay(transaction.category, locale)}
        </div>
        <div className="activity-sub">
          {categoryDisplay(transaction.category, locale)} / {transaction.date}
        </div>
      </div>
      <span style={{ color, flexShrink: 0, fontSize: 12.5, fontWeight: 800 }}>
        {transaction.type === "income" ? "+" : "-"}
        {format(transaction.amount)}
      </span>
    </div>
  );
}
