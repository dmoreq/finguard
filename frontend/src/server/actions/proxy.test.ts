import { describe, expect, it, vi } from "vitest";
import { getActionsUrl, mirrorActionsResponse, proxyToActions } from "./proxy";

describe("getActionsUrl", () => {
  it("uses ACTIONS_URL when set", () => {
    vi.stubEnv("ACTIONS_URL", "http://actions:5055");
    expect(getActionsUrl()).toBe("http://actions:5055");
    vi.unstubAllEnvs();
  });

  it("falls back to localhost when unset", () => {
    vi.stubEnv("ACTIONS_URL", "");
    expect(getActionsUrl()).toBe("http://127.0.0.1:5055");
    vi.unstubAllEnvs();
  });
});

describe("proxyToActions", () => {
  it("returns 503 when upstream is unreachable", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("ECONNREFUSED"));

    const response = await proxyToActions("/data/transactions");
    expect(response.status).toBe(503);
    const body = await response.json();
    expect(body.error?.code).toBe("ACTIONS_UNAVAILABLE");

    vi.mocked(globalThis.fetch).mockRestore();
  });
});

describe("mirrorActionsResponse", () => {
  it("preserves status and content type", async () => {
    const upstream = new Response('{"ok":true}', {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
    const mirrored = await mirrorActionsResponse(upstream);
    expect(mirrored.status).toBe(201);
    expect(await mirrored.json()).toEqual({ ok: true });
  });

  it("mirrors non-JSON upstream bodies", async () => {
    const upstream = new Response("plain", { status: 502 });
    const mirrored = await mirrorActionsResponse(upstream);
    expect(mirrored.status).toBe(502);
    expect(await mirrored.text()).toBe("plain");
  });
});
