import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cx, formatMoney, formatPlainMoney, formatTransactionDate, todayISO } from "./format";

describe("formatMoney", () => {
  it("formats USD with two decimals", () => {
    expect(formatMoney(1234.5)).toBe("$1,234.50");
  });

  it("treats non-finite values as zero", () => {
    expect(formatMoney(Number.NaN)).toBe("$0.00");
  });

  it("uses compact notation for large amounts", () => {
    expect(formatMoney(1500, { compact: true })).toBe("$1.5k");
    expect(formatMoney(12000, { compact: true })).toBe("$12k");
  });

  it("does not compact amounts under 1000", () => {
    expect(formatMoney(999, { compact: true })).toBe("$999.00");
  });
});

describe("formatPlainMoney", () => {
  it("formats without currency symbol", () => {
    expect(formatPlainMoney(42)).toBe("42.00");
  });

  it("treats non-finite values as zero", () => {
    expect(formatPlainMoney(Number.POSITIVE_INFINITY)).toBe("0.00");
  });
});

describe("todayISO", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-05-28T15:30:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns the current UTC date", () => {
    expect(todayISO()).toBe("2026-05-28");
  });
});

describe("formatTransactionDate", () => {
  it('returns "Today" when value is missing', () => {
    expect(formatTransactionDate(null)).toBe("Today");
    expect(formatTransactionDate(undefined)).toBe("Today");
  });

  it("formats ISO dates for display", () => {
    expect(formatTransactionDate("2026-05-15")).toMatch(/May/);
    expect(formatTransactionDate("2026-05-15")).toMatch(/2026/);
  });
});

describe("cx", () => {
  it("joins truthy class names", () => {
    expect(cx("a", false && "b", null, "c")).toBe("a c");
  });

  it("returns empty string when all parts are falsy", () => {
    expect(cx(false, null, undefined)).toBe("");
  });
});
