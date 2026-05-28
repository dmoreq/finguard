import { LOCAL_USER_ID } from "@/lib/constants";
import { describe, expect, it, vi } from "vitest";
import { getRasaUrl, resolveChatUserId } from "./resolve-user";

describe("resolveChatUserId", () => {
  it("returns the local dev user id", async () => {
    await expect(resolveChatUserId()).resolves.toBe(LOCAL_USER_ID);
  });
});

describe("getRasaUrl", () => {
  it("returns trimmed RASA_URL", () => {
    vi.stubEnv("RASA_URL", "  http://localhost:5005  ");
    expect(getRasaUrl()).toBe("http://localhost:5005");
    vi.unstubAllEnvs();
  });

  it("returns null for empty RASA_URL", () => {
    vi.stubEnv("RASA_URL", "   ");
    expect(getRasaUrl()).toBeNull();
    vi.unstubAllEnvs();
  });
});
