export function formatMoney(value: number, options?: { compact?: boolean; currency?: string }) {
  const amount = Number.isFinite(value) ? value : 0;
  const currency = options?.currency ?? "USD";

  if (options?.compact && Math.abs(amount) >= 1000) {
    const symbol = currency === "VND" ? "₫" : "$";
    return `${symbol}${(amount / 1000).toFixed(amount >= 10000 ? 0 : 1)}k`;
  }

  if (currency === "VND") {
    return `${amount.toLocaleString("vi-VN", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    })}₫`;
  }

  return amount.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function formatPlainMoney(value: number, currency?: string) {
  return (Number.isFinite(value) ? value : 0).toLocaleString(
    currency === "VND" ? "vi-VN" : "en-US",
    {
      minimumFractionDigits: currency === "VND" ? 0 : 2,
      maximumFractionDigits: currency === "VND" ? 0 : 2,
    },
  );
}

export function todayISO() {
  return new Date().toISOString().split("T")[0] ?? "";
}

export function formatTransactionDate(value?: string | null) {
  if (!value) return "Today";

  try {
    return new Date(`${value}T12:00:00`).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return value;
  }
}

export function cx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}
