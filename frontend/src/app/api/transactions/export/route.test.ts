import { describe, expect, it, vi } from "vitest";

vi.mock("@/server/actions/proxy", () => ({
  proxyToActions: vi.fn(),
}));

import { proxyToActions } from "@/server/actions/proxy";
import { GET } from "./route";

describe("GET /api/transactions/export", () => {
  it("returns CSV header and escaped fields", async () => {
    vi.mocked(proxyToActions).mockResolvedValue(
      new Response(
        JSON.stringify([
          {
            id: "tx-1",
            type: "expense",
            amount: 10,
            currency: "USD",
            category: "food",
            description: 'coffee, "special"',
            transaction_date: "2026-05-15",
            status: "confirmed",
            created_at: "2026-05-15T00:00:00Z",
          },
        ]),
        { status: 200 },
      ),
    );

    const response = await GET();
    expect(response.status).toBe(200);
    const csv = await response.text();
    expect(csv.split("\n")[0]).toContain("id,type,amount");
    expect(csv).toContain('"coffee, ""special"""');
  });

  it("returns header only when no transactions", async () => {
    vi.mocked(proxyToActions).mockResolvedValue(new Response("[]", { status: 200 }));

    const response = await GET();
    const csv = await response.text();
    const lines = csv.trim().split("\n");
    expect(lines).toHaveLength(1);
  });

  it("returns 500 when upstream fails", async () => {
    vi.mocked(proxyToActions).mockResolvedValue(new Response("error", { status: 503 }));

    const response = await GET();
    expect(response.status).toBe(500);
    const body = await response.json();
    expect(body.error?.code).toBe("EXPORT_FAILED");
  });
});
