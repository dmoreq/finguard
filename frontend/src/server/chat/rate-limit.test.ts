import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { checkChatRateLimit } from "./rate-limit";

describe("checkChatRateLimit", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-05-15T12:00:00Z"));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("allows up to 60 requests per minute", () => {
    const userId = `user-${Math.random()}`;
    for (let i = 0; i < 60; i += 1) {
      expect(checkChatRateLimit(userId).allowed).toBe(true);
    }
    const blocked = checkChatRateLimit(userId);
    expect(blocked.allowed).toBe(false);
    expect(blocked.retryAfterSec).toBeGreaterThan(0);
  });

  it("resets after the window elapses", () => {
    const userId = `user-reset-${Math.random()}`;
    for (let i = 0; i < 60; i += 1) {
      checkChatRateLimit(userId);
    }
    expect(checkChatRateLimit(userId).allowed).toBe(false);

    vi.advanceTimersByTime(61_000);
    expect(checkChatRateLimit(userId).allowed).toBe(true);
  });
});
