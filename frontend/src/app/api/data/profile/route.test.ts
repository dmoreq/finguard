import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/actions/proxy", () => ({
  proxyToActions: vi.fn(),
  mirrorActionsResponse: vi.fn(),
}));

import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";
import { GET, PATCH } from "./route";

describe("/api/data/profile", () => {
  beforeEach(() => {
    vi.mocked(proxyToActions).mockReset();
    vi.mocked(mirrorActionsResponse).mockReset();
  });

  it("GET proxies to action server", async () => {
    const upstream = new Response(JSON.stringify({ currency: "USD" }), { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await GET();

    expect(proxyToActions).toHaveBeenCalledWith("/data/profile");
  });

  it("PATCH forwards body to action server", async () => {
    const upstream = new Response(JSON.stringify({ currency: "EUR" }), { status: 200 });
    vi.mocked(proxyToActions).mockResolvedValue(upstream);
    vi.mocked(mirrorActionsResponse).mockResolvedValue(upstream);

    await PATCH(
      new Request("http://localhost/api/data/profile", {
        method: "PATCH",
        body: JSON.stringify({ currency: "EUR" }),
      }),
    );

    expect(proxyToActions).toHaveBeenCalledWith(
      "/data/profile",
      expect.objectContaining({ method: "PATCH" }),
    );
  });
});
