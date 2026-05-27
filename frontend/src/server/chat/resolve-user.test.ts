import { afterEach, describe, expect, it, vi } from "vitest";

describe("resolveChatUserId", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("returns null when Supabase is not configured", async () => {
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "");

    const { resolveChatUserId } = await import("./resolve-user");
    await expect(resolveChatUserId()).resolves.toBeNull();
  });
});
