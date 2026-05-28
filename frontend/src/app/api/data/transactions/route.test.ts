import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/actions/proxy", () => ({
  proxyToActions: vi.fn(),
  mirrorActionsResponse: vi.fn(),
}));

import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";
import { DELETE, GET } from "./route";

describe("/api/data/transactions", () => {
  beforeEach(() => {
    vi.mocked(proxyToActions).mockReset();
    vi.mocked(mirrorActionsResponse).mockReset();
  });

  it("GET proxies to action server", async () => {
    const upstream = new Response("[]", { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(new Response("[]", { status: 200 }));

    await GET();

    expect(proxyToActions).toHaveBeenCalledWith("/data/transactions");
    expect(mirrorActionsResponse).toHaveBeenCalledWith(upstream);
  });

  it("DELETE proxies to action server", async () => {
    const upstream = new Response('{"ok":true}', { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(
      new Response('{"ok":true}', { status: 200 }),
    );

    await DELETE();

    expect(proxyToActions).toHaveBeenCalledWith("/data/transactions", { method: "DELETE" });
  });
});
