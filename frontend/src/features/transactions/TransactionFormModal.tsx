"use client";

import type { Transaction } from "@/features/transactions/types";
import { CATEGORY_OPTIONS } from "@/lib/categories";
import { todayISO } from "@/lib/format";
import { useEffect, useState } from "react";

type Props = {
  locale?: string;
  initial?: Partial<Transaction> & { id?: string };
  onSave: (payload: {
    id?: string;
    type: "income" | "expense";
    amount: number;
    category: string;
    description?: string;
    transaction_date: string;
  }) => Promise<void>;
  onClose: () => void;
};

export function TransactionFormModal({ locale = "vi", initial, onSave, onClose }: Props) {
  const isVi = locale.startsWith("vi");
  const [type, setType] = useState<"income" | "expense">(
    initial?.type === "income" ? "income" : "expense",
  );
  const [amount, setAmount] = useState(initial?.amount?.toString() ?? "");
  const [category, setCategory] = useState(initial?.category?.toLowerCase() ?? "dining");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [date, setDate] = useState(initial?.date ?? todayISO());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initial?.category) setCategory(initial.category.toLowerCase());
  }, [initial]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    const parsed = Number(amount);
    if (!parsed || parsed <= 0) {
      setError(isVi ? "Nhập số tiền hợp lệ." : "Enter a valid amount.");
      return;
    }
    setSaving(true);
    try {
      await onSave({
        id: initial?.id,
        type,
        amount: parsed,
        category,
        description: description.trim() || undefined,
        transaction_date: date,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : isVi ? "Không lưu được." : "Could not save.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <h3>
          {initial?.id
            ? isVi
              ? "Sửa giao dịch"
              : "Edit transaction"
            : isVi
              ? "Thêm giao dịch"
              : "Add transaction"}
        </h3>
        <label className="login-label">{isVi ? "Loại" : "Type"}</label>
        <select
          className="login-input"
          value={type}
          onChange={(e) => setType(e.target.value as "income" | "expense")}
        >
          <option value="expense">{isVi ? "Chi" : "Expense"}</option>
          <option value="income">{isVi ? "Thu" : "Income"}</option>
        </select>
        <label className="login-label">{isVi ? "Số tiền" : "Amount"}</label>
        <input
          className="login-input"
          type="number"
          min="0"
          step="0.01"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          required
        />
        <label className="login-label">{isVi ? "Danh mục" : "Category"}</label>
        <select
          className="login-input"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          {CATEGORY_OPTIONS.map((opt) => (
            <option key={opt.slug} value={opt.slug}>
              {isVi ? opt.vi : opt.en}
            </option>
          ))}
        </select>
        <label className="login-label">{isVi ? "Mô tả" : "Description"}</label>
        <input
          className="login-input"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <label className="login-label">{isVi ? "Ngày" : "Date"}</label>
        <input
          className="login-input"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
        {error && <p className="login-error">{error}</p>}
        <div className="modal-actions">
          <button type="button" className="button button-ghost" onClick={onClose}>
            {isVi ? "Hủy" : "Cancel"}
          </button>
          <button type="submit" className="button button-primary" disabled={saving}>
            {saving ? (isVi ? "Đang lưu…" : "Saving…") : isVi ? "Lưu" : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}
