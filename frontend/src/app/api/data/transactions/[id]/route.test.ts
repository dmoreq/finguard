import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/actions/proxy", () => ({
  proxyToActions: vi.fn(),
  mirrorActionsResponse: vi.fn(),
}));

import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";
import { DELETE, PATCH } from "./route";

describe("/api/data/transactions/[id]", () => {
  beforeEach(() => {
    vi.mocked(proxyToActions).mockReset();
    vi.mocked(mirrorActionsResponse).mockReset();
  });

  it("PATCH proxies partial update", async () => {
    const upstream = new Response('{"id":"tx-1","amount":50}', { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await PATCH(
      new Request("http://localhost/api/data/transactions/tx-1", {
        method: "PATCH",
        body: JSON.stringify({ amount: 50 }),
      }),
      { params: Promise.resolve({ id: "tx-1" }) },
    );

    expect(proxyToActions).toHaveBeenCalledWith("/data/transactions/tx-1", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ amount: 50 }),
    });
  });

  it("DELETE proxies single transaction delete", async () => {
    const upstream = new Response('{"ok":true}', { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await DELETE(new Request("http://localhost/api/data/transactions/tx-1"), {
      params: Promise.resolve({ id: "tx-1" }),
    });

    expect(proxyToActions).toHaveBeenCalledWith("/data/transactions/tx-1", { method: "DELETE" });
  });
});
