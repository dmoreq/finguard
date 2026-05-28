import { describe, expect, it } from "vitest";
import { parseChatRequest } from "./schemas";

describe("parseChatRequest", () => {
  it("accepts a trimmed message", () => {
    expect(parseChatRequest({ message: "  hello  " })).toEqual({ message: "hello" });
  });

  it("rejects missing message", () => {
    expect(() => parseChatRequest({})).toThrow("Invalid message");
  });

  it("rejects non-string message", () => {
    expect(() => parseChatRequest({ message: 42 })).toThrow("Invalid message");
  });

  it("rejects whitespace-only message", () => {
    expect(() => parseChatRequest({ message: "   " })).toThrow("Invalid message");
  });

  it("rejects message over 2000 characters", () => {
    expect(() => parseChatRequest({ message: "x".repeat(2001) })).toThrow("Invalid message");
  });

  it("rejects non-object body", () => {
    expect(() => parseChatRequest(null)).toThrow("Invalid request body");
  });
});
