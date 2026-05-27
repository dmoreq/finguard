"use client";

import { formatTransactionDate } from "@/lib/format";
import { cx } from "@/lib/format";
import { useState } from "react";
import type { ReactNode } from "react";
import {
  type Transaction,
  type TransactionStatus,
  type TransactionType,
  categories,
  transactionConfig,
} from "./types";

type Props = {
  transaction: Transaction;
  txStatus?: TransactionStatus;
  onConfirm: (transaction: Transaction) => void;
  onCancel: () => void;
};

export function TransactionCard({
  transaction,
  txStatus = "pending_confirmation",
  onConfirm,
  onCancel,
}: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState<Transaction>({ ...transaction });
  const config = transactionConfig[draft.type];
  const isPending = txStatus === "pending_confirmation";

  const update = <K extends keyof Transaction>(key: K, value: Transaction[K]) => {
    setDraft((current) => ({ ...current, [key]: value }));
  };

  const changeType = (type: TransactionType) => {
    setDraft((current) => ({
      ...current,
      type,
      category: categories[type].includes(current.category)
        ? current.category
        : (categories[type][0] ?? "Other"),
    }));
  };

  const resetDraft = () => {
    setDraft({ ...transaction });
    setIsEditing(false);
  };

  return (
    <div
      className={cx(
        "tx-card",
        txStatus === "confirmed" && "saved",
        txStatus === "discarded" && "discarded",
      )}
      style={{ borderColor: config.accent }}
    >
      <div className="tx-stripe" style={{ background: config.accent }} />
      <div className="tx-head" style={{ background: config.bg }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 5 }}>
            <span className="badge" style={{ background: config.accent }}>
              {config.badge}
            </span>
            {txStatus === "confirmed" && (
              <span style={{ color: config.accent, fontSize: 11, fontWeight: 800 }}>Saved</span>
            )}
            {txStatus === "discarded" && (
              <span style={{ color: "var(--text-muted)", fontSize: 11, fontWeight: 700 }}>
                Discarded
              </span>
            )}
          </div>
          <div style={{ color: "oklch(0.48 0.02 250)", fontSize: 13, fontWeight: 600 }}>
            {draft.category}
          </div>
        </div>
        <div>
          <div className="tx-amount" style={{ color: config.dark }}>
            {config.sign}${Number(draft.amount || 0).toFixed(2)}
          </div>
          {isPending && (
            <button
              className="button"
              onClick={() => setIsEditing((current) => !current)}
              style={{
                borderColor: config.accent,
                color: isEditing ? "#fff" : config.accent,
                background: isEditing ? config.accent : "transparent",
                marginTop: 5,
                padding: "3px 9px",
              }}
            >
              {isEditing ? "Close" : "Edit"}
            </button>
          )}
        </div>
      </div>

      {isEditing && isPending ? (
        <div
          style={{
            borderTop: `1px solid ${config.accent}28`,
            background: "oklch(0.99 0.003 250)",
            padding: "12px 16px 4px",
          }}
        >
          <FieldLabel>Transaction Type</FieldLabel>
          <div style={{ display: "flex", gap: 5, marginBottom: 12 }}>
            {(["income", "expense", "pending"] as const).map((type) => (
              <button
                key={type}
                className="button"
                onClick={() => changeType(type)}
                style={{
                  flex: 1,
                  borderColor:
                    draft.type === type ? transactionConfig[type].accent : "var(--border-strong)",
                  background: draft.type === type ? transactionConfig[type].accent : "transparent",
                  color: draft.type === type ? "#fff" : "var(--text-soft)",
                  padding: "6px 4px",
                }}
              >
                {transactionConfig[type].badge}
              </button>
            ))}
          </div>

          <FieldLabel>Amount ($)</FieldLabel>
          <input
            className="field"
            type="number"
            min="0"
            step="0.01"
            value={draft.amount}
            onChange={(event) => update("amount", Number.parseFloat(event.target.value) || 0)}
          />

          <FieldLabel>Category</FieldLabel>
          <select
            className="field"
            value={draft.category}
            onChange={(event) => update("category", event.target.value)}
          >
            {categories[draft.type].map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>

          <FieldLabel>Description</FieldLabel>
          <input
            className="field"
            type="text"
            value={draft.description ?? ""}
            onChange={(event) => update("description", event.target.value)}
            placeholder="What was this for?"
          />

          <FieldLabel>Date</FieldLabel>
          <input
            className="field"
            type="date"
            value={draft.date}
            onChange={(event) => update("date", event.target.value)}
          />

          <div style={{ display: "flex", gap: 7, paddingBottom: 12 }}>
            <button
              className="button button-primary"
              onClick={() => setIsEditing(false)}
              style={{ flex: 1, background: config.accent, padding: "8px 0" }}
            >
              Apply Changes
            </button>
            <button
              className="button button-ghost"
              onClick={resetDraft}
              style={{ padding: "8px 14px" }}
            >
              Reset
            </button>
          </div>
        </div>
      ) : (
        <div className="tx-body">
          {draft.description && (
            <p
              style={{
                color: "oklch(0.32 0.015 250)",
                fontSize: 13,
                lineHeight: 1.55,
                margin: "0 0 7px",
              }}
            >
              {draft.description}
            </p>
          )}
          <div style={{ color: "var(--text-muted)", fontSize: 12 }}>
            {formatTransactionDate(draft.date)}
          </div>
        </div>
      )}

      {isPending && (
        <div className="tx-actions">
          <button
            className="button button-primary"
            onClick={() => onConfirm(draft)}
            style={{ flex: 1, background: config.accent, padding: "9px 0" }}
          >
            Save Transaction
          </button>
          <button
            className="button button-ghost"
            onClick={onCancel}
            style={{ padding: "9px 14px" }}
          >
            Discard
          </button>
        </div>
      )}
    </div>
  );
}

function FieldLabel({ children }: { children: ReactNode }) {
  return <div className="field-label">{children}</div>;
}
