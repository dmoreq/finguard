import { formatPlainMoney } from "@/lib/format";
import type { ReportData } from "./finance-calculations";

type Props = {
  data: ReportData;
};

export function ReportCard({ data }: Props) {
  const spentPct =
    data.totalIncome > 0
      ? Math.min(100, Math.round((data.totalExpenses / data.totalIncome) * 100))
      : 0;
  const netPositive = data.net >= 0;

  return (
    <div
      className="report-card"
      style={{
        border: `1.5px solid ${netPositive ? "oklch(0.82 0.09 165)" : "oklch(0.86 0.07 22)"}`,
      }}
    >
      <div
        style={{
          background: "linear-gradient(135deg, oklch(0.48 0.20 165), oklch(0.55 0.17 190))",
          padding: 18,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
          <div>
            <div className="stat-label" style={{ color: "oklch(0.82 0.09 165)", marginBottom: 5 }}>
              Financial Snapshot / {data.monthLabel}
            </div>
            <div
              style={{
                color: "#fff",
                fontFamily: "Sora, sans-serif",
                fontSize: 32,
                fontWeight: 800,
                lineHeight: 1,
              }}
            >
              {netPositive ? "+" : "-"}${formatPlainMoney(Math.abs(data.net))}
            </div>
            <div style={{ color: "oklch(0.86 0.07 165)", fontSize: 12, marginTop: 6 }}>
              {data.txCount} transaction{data.txCount !== 1 ? "s" : ""} this month
            </div>
          </div>
          {data.savingsRate !== null && (
            <div
              style={{
                alignSelf: "flex-start",
                border: "1px solid oklch(1 0 0 / 0.15)",
                borderRadius: 12,
                background: "oklch(0 0 0 / 0.18)",
                padding: "8px 14px",
                textAlign: "center",
              }}
            >
              <div
                style={{
                  color: "#fff",
                  fontFamily: "Sora, sans-serif",
                  fontSize: 22,
                  fontWeight: 800,
                  lineHeight: 1,
                }}
              >
                {data.savingsRate}%
              </div>
              <div className="stat-label" style={{ color: "oklch(0.86 0.07 165)", marginTop: 3 }}>
                saved
              </div>
            </div>
          )}
        </div>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 1,
          background: "oklch(0.91 0.007 250)",
        }}
      >
        <StatCell
          label="Income"
          value={`+$${formatPlainMoney(data.totalIncome)}`}
          color="oklch(0.34 0.15 145)"
          bg="oklch(0.97 0.025 145)"
        />
        <StatCell
          label="Expenses"
          value={`-$${formatPlainMoney(data.totalExpenses)}`}
          color="oklch(0.42 0.13 22)"
          bg="oklch(0.97 0.02 22)"
        />
        <StatCell
          label="Daily Burn"
          value={data.dailySpend > 0 ? `$${data.dailySpend.toFixed(2)}/d` : "-"}
          color="oklch(0.45 0.15 265)"
          bg="#fff"
        />
        <StatCell
          label="Pending"
          value={data.pendingCount > 0 ? `$${formatPlainMoney(data.pendingTotal)}` : "None"}
          color="oklch(0.50 0.13 72)"
          bg="#fff"
        />
      </div>
      {data.totalIncome > 0 && (
        <div
          style={{
            borderTop: "1px solid var(--border)",
            background: "#fff",
            padding: "12px 16px 14px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 7 }}>
            <span style={{ color: "oklch(0.42 0.015 250)", fontSize: 11.5, fontWeight: 700 }}>
              {spentPct}% of income spent
            </span>
            {data.topCategory && (
              <span
                style={{
                  borderRadius: 20,
                  background: "oklch(0.96 0.025 22)",
                  color: "oklch(0.46 0.13 22)",
                  padding: "2px 9px",
                  fontSize: 10.5,
                  fontWeight: 800,
                }}
              >
                Top: {data.topCategory}
              </span>
            )}
          </div>
          <div className="bar-track" style={{ height: 8 }}>
            <div
              className="bar-fill"
              style={{
                width: `${spentPct}%`,
                background:
                  spentPct > 90
                    ? "var(--expense)"
                    : spentPct > 70
                      ? "var(--pending)"
                      : "var(--primary)",
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function StatCell({
  label,
  value,
  color,
  bg,
}: { label: string; value: string; color: string; bg: string }) {
  return (
    <div style={{ background: bg, padding: "12px 16px" }}>
      <div className="stat-label" style={{ marginBottom: 3 }}>
        {label}
      </div>
      <div
        style={{
          color,
          fontFamily: "Sora, sans-serif",
          fontSize: 15,
          fontWeight: 800,
          lineHeight: 1.2,
        }}
      >
        {value}
      </div>
    </div>
  );
}
