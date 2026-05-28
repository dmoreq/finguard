import { LOCAL_USER_ID } from "@/lib/constants";
import { describe, expect, it, vi } from "vitest";
import { getChatBackendUrl, getRasaUrl, resolveChatUserId } from "./resolve-user";

describe("resolveChatUserId", () => {
  it("returns the local dev user id", async () => {
    await expect(resolveChatUserId()).resolves.toBe(LOCAL_USER_ID);
  });
});

describe("getChatBackendUrl", () => {
  it("returns trimmed CHAT_BACKEND_URL", () => {
    vi.stubEnv("CHAT_BACKEND_URL", "  http://localhost:5055  ");
    vi.stubEnv("RASA_URL", "");
    expect(getChatBackendUrl()).toBe("http://localhost:5055");
    vi.unstubAllEnvs();
  });

  it("falls back to RASA_URL", () => {
    vi.stubEnv("CHAT_BACKEND_URL", "");
    vi.stubEnv("RASA_URL", "http://localhost:5055");
    expect(getChatBackendUrl()).toBe("http://localhost:5055");
    vi.unstubAllEnvs();
  });

  it("returns null when unset", () => {
    vi.stubEnv("CHAT_BACKEND_URL", "   ");
    vi.stubEnv("RASA_URL", "   ");
    expect(getChatBackendUrl()).toBeNull();
    vi.unstubAllEnvs();
  });
});

describe("getRasaUrl", () => {
  it("delegates to getChatBackendUrl", () => {
    vi.stubEnv("CHAT_BACKEND_URL", "http://localhost:5055");
    expect(getRasaUrl()).toBe("http://localhost:5055");
    vi.unstubAllEnvs();
  });
});
