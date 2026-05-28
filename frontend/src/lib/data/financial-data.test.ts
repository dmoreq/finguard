import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { clearAllTransactions, fetchUserTransactions } from "./financial-data";

describe("financial-data", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify([
            {
              id: "tx-1",
              type: "expense",
              amount: 12,
              category: "food",
              description: null,
              transaction_date: "2026-05-15",
              status: "confirmed",
            },
          ]),
          { status: 200 },
        ),
      ),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetchUserTransactions maps API rows", async () => {
    const rows = await fetchUserTransactions();
    expect(rows).toHaveLength(1);
    expect(rows[0]?.amount).toBe(12);
    expect(rows[0]?.category).toBe("Food");
    expect(rows[0]?.date).toBe("2026-05-15");
  });

  it("throws actionable error when actions are unavailable", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "ACTIONS_UNAVAILABLE", message: "run make dev" },
        }),
        { status: 503 },
      ),
    );
    await expect(fetchUserTransactions()).rejects.toThrow("run make dev");
  });

  it("clearAllTransactions calls DELETE", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response("{}", { status: 200 }));
    await clearAllTransactions();
    expect(fetch).toHaveBeenCalledWith("/api/data/transactions", { method: "DELETE" });
  });
});
