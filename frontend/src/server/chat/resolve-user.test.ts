import { afterEach, describe, expect, it, vi } from "vitest";

describe("resolveChatUserId", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it("returns dev user id when dev fallback is enabled", async () => {
    vi.stubEnv("ENABLE_DEV_USER_FALLBACK", "true");
    vi.stubEnv("FIN_GUARD_DEV_USER_ID", "00000000-0000-0000-0000-000000000001");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "");

    const { resolveChatUserId } = await import("./resolve-user");
    await expect(resolveChatUserId()).resolves.toBe("00000000-0000-0000-0000-000000000001");
  });

  it("returns null when neither auth nor dev fallback is configured", async () => {
    vi.stubEnv("ENABLE_DEV_USER_FALLBACK", "false");
    vi.stubEnv("NEXT_PUBLIC_SUPABASE_URL", "");

    const { resolveChatUserId } = await import("./resolve-user");
    await expect(resolveChatUserId()).resolves.toBeNull();
  });
});
