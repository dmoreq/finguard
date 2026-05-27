import type { TransactionRow } from "@/lib/data/map-db-row";
import { createServerSupabaseClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

function escapeCsv(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
}

export async function GET() {
  const supabase = await createServerSupabaseClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json(
      { error: { code: "UNAUTHORIZED", message: "Sign in to export." } },
      { status: 401 },
    );
  }

  const { data, error } = await supabase
    .from("transactions")
    .select(
      "id, type, amount, currency, category, description, transaction_date, status, created_at",
    )
    .eq("user_id", user.id)
    .neq("status", "discarded")
    .order("transaction_date", { ascending: false });

  if (error) {
    return NextResponse.json(
      { error: { code: "EXPORT_FAILED", message: error.message } },
      { status: 500 },
    );
  }

  const header = [
    "id",
    "type",
    "amount",
    "currency",
    "category",
    "description",
    "transaction_date",
    "status",
    "created_at",
  ];
  const rows = (
    (data ?? []) as Pick<
      TransactionRow,
      | "id"
      | "type"
      | "amount"
      | "currency"
      | "category"
      | "description"
      | "transaction_date"
      | "status"
      | "created_at"
    >[]
  ).map((row) =>
    [
      row.id,
      row.type,
      row.amount,
      row.currency,
      row.category,
      row.description ?? "",
      row.transaction_date,
      row.status,
      row.created_at,
    ]
      .map((cell) => escapeCsv(String(cell)))
      .join(","),
  );

  const csv = [header.join(","), ...rows].join("\n");

  return new NextResponse(csv, {
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": 'attachment; filename="finguard-transactions.csv"',
    },
  });
}
