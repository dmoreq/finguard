import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/actions/proxy", () => ({
  proxyToActions: vi.fn(),
  mirrorActionsResponse: vi.fn(),
}));

import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";
import { GET, POST } from "./route";

describe("/api/data/backup", () => {
  beforeEach(() => {
    vi.mocked(proxyToActions).mockReset();
    vi.mocked(mirrorActionsResponse).mockReset();
  });

  it("GET proxies backup download", async () => {
    const upstream = new Response('{"transactions":[]}', { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await GET();

    expect(proxyToActions).toHaveBeenCalledWith("/data/backup");
    expect(mirrorActionsResponse).toHaveBeenCalledWith(upstream);
  });

  it("POST proxies restore payload", async () => {
    const upstream = new Response('{"ok":true}', { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await POST(
      new Request("http://localhost/api/data/backup", {
        method: "POST",
        body: JSON.stringify({ transactions: [] }),
      }),
    );

    expect(proxyToActions).toHaveBeenCalledWith("/data/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions: [] }),
    });
  });
});
