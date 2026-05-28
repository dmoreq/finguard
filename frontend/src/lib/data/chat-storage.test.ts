import type { ChatMessage } from "@/features/chat/types";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { clearChatMessages, loadChatMessages, saveChatMessages } from "./chat-storage";

const sample: ChatMessage = {
  id: "m1",
  role: "user",
  type: "text",
  content: "hello",
  timestamp: "2026-05-15T00:00:00Z",
};

describe("chat-storage", () => {
  const store = new Map<string, string>();

  beforeEach(() => {
    store.clear();
    vi.stubGlobal("window", {} as Window);
    vi.stubGlobal("localStorage", {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => {
        store.set(key, value);
      },
      removeItem: (key: string) => {
        store.delete(key);
      },
    });
  });

  it("round-trips messages", () => {
    saveChatMessages([sample]);
    expect(loadChatMessages()).toEqual([sample]);
  });

  it("returns empty array when storage is empty", () => {
    expect(loadChatMessages()).toEqual([]);
  });

  it("returns empty array for corrupt JSON", () => {
    store.set("finguard.chat.messages", "{not-json");
    expect(loadChatMessages()).toEqual([]);
  });

  it("clearChatMessages removes data", () => {
    saveChatMessages([sample]);
    clearChatMessages();
    expect(loadChatMessages()).toEqual([]);
  });
});
