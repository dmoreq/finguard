import { categoryDisplay } from "@/lib/categories";
import { proxyToActions } from "@/server/actions/proxy";
import { NextResponse } from "next/server";

function escapeCsv(value: string): string {
  if (value.includes(",") || value.includes('"') || value.includes("\n")) {
    return `"${value.replaceAll('"', '""')}"`;
  }
  return value;
}

export async function GET() {
  const response = await proxyToActions("/data/transactions");
  if (!response.ok) {
    return NextResponse.json(
      { error: { code: "EXPORT_FAILED", message: "Could not load transactions." } },
      { status: 500 },
    );
  }

  const data = (await response.json()) as Array<Record<string, unknown>>;
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
  const rows = data.map((row) =>
    [
      row.id,
      row.type,
      row.amount,
      row.currency,
      categoryDisplay(String(row.category ?? "")),
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
