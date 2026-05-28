import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/server/chat/resolve-user", () => ({
  resolveChatUserId: vi.fn(),
  getChatBackendUrl: vi.fn(),
  getRasaUrl: vi.fn(),
}));

import { getChatBackendUrl, resolveChatUserId } from "@/server/chat/resolve-user";
import { POST } from "./route";

describe("POST /api/chat", () => {
  beforeEach(() => {
    vi.mocked(resolveChatUserId).mockReset();
    vi.mocked(getChatBackendUrl).mockReset();
    vi.mocked(resolveChatUserId).mockResolvedValue("local-user");
  });

  it("returns 503 when CHAT_BACKEND_URL is not set", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue(null);

    const response = await POST(
      new Request("http://localhost/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "spent 5 on tea" }),
      }),
    );

    expect(response.status).toBe(503);
    const body = await response.json();
    expect(body.error?.code).toBe("CHAT_NOT_CONFIGURED");
  });

  it("proxies to chat backend when configured", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue("http://localhost:5055");

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
      "http://localhost:5055/webhooks/rest/webhook",
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

  it("returns 503 when chat backend fetch fails", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue("http://localhost:5055");
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
    expect(body.error?.code).toBe("CHAT_UNAVAILABLE");

    vi.mocked(globalThis.fetch).mockRestore();
  });

  it("returns 503 when chat backend responds with HTTP error", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue("http://localhost:5055");
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
    expect(body.error?.code).toBe("CHAT_UNAVAILABLE");

    vi.mocked(globalThis.fetch).mockRestore();
  });

  it("returns 400 for invalid JSON body", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue("http://localhost:5055");

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

  it("returns 500 when chat backend returns non-JSON", async () => {
    vi.mocked(getChatBackendUrl).mockReturnValue("http://localhost:5055");
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
