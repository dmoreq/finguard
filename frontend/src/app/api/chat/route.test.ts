import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/chat/resolve-user", () => ({
  resolveChatUserId: vi.fn(),
  getRasaUrl: vi.fn(),
}));

import { getRasaUrl, resolveChatUserId } from "@/server/chat/resolve-user";
import { POST } from "./route";

describe("POST /api/chat", () => {
  beforeEach(() => {
    vi.mocked(resolveChatUserId).mockReset();
    vi.mocked(getRasaUrl).mockReset();
    vi.mocked(resolveChatUserId).mockResolvedValue("local-user");
  });

  it("returns 503 when RASA_URL is not set", async () => {
    vi.mocked(getRasaUrl).mockReturnValue(null);

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "spent 5 on tea" }),
      }),
    );

    expect(response.status).toBe(503);
    const body = await response.json();
    expect(body.error?.code).toBe("RASA_NOT_CONFIGURED");
  });

  it("proxies to Rasa when configured", async () => {
    vi.mocked(getRasaUrl).mockReturnValue("http://localhost:5005");

    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValue(new Response(JSON.stringify([{ text: "Hi there" }]), { status: 200 }));

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hello" }),
      }),
    );

    expect(response.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:5005/webhooks/rest/webhook",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          sender: "local-user",
          message: "hello",
          metadata: { user_id: "local-user" },
        }),
      }),
    );

    fetchMock.mockRestore();
  });

  it("returns 503 when Rasa fetch fails", async () => {
    vi.mocked(getRasaUrl).mockReturnValue("http://localhost:5005");
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("ECONNREFUSED"));

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hello" }),
      }),
    );

    expect(response.status).toBe(503);
    const body = await response.json();
    expect(body.error?.code).toBe("RASA_UNAVAILABLE");

    vi.mocked(globalThis.fetch).mockRestore();
  });

  it("returns 503 when Rasa responds with HTTP error", async () => {
    vi.mocked(getRasaUrl).mockReturnValue("http://localhost:5005");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("upstream error", { status: 500 }),
    );

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hello" }),
      }),
    );

    expect(response.status).toBe(503);
    const body = await response.json();
    expect(body.error?.code).toBe("RASA_UNAVAILABLE");

    vi.mocked(globalThis.fetch).mockRestore();
  });

  it("returns 400 for invalid JSON body", async () => {
    vi.mocked(getRasaUrl).mockReturnValue("http://localhost:5005");

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "" }),
      }),
    );

    expect(response.status).toBe(400);
    const body = await response.json();
    expect(body.error?.code).toBe("VALIDATION_ERROR");
  });

  it("returns 500 when Rasa returns non-JSON", async () => {
    vi.mocked(getRasaUrl).mockReturnValue("http://localhost:5005");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("not json", { status: 200, headers: { "Content-Type": "text/plain" } }),
    );

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "hello" }),
      }),
    );

    expect(response.status).toBe(500);
    const body = await response.json();
    expect(body.error?.code).toBe("INTERNAL_ERROR");

    vi.mocked(globalThis.fetch).mockRestore();
  });
});
