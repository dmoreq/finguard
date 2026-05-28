import { LOCAL_USER_ID } from "@/lib/constants";
import { describe, expect, it } from "vitest";
import { resolveChatUserId } from "./resolve-user";

describe("resolveChatUserId", () => {
  it("returns the local dev user id", async () => {
    await expect(resolveChatUserId()).resolves.toBe(LOCAL_USER_ID);
  });
});
