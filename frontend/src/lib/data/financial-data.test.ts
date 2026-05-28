import type { ChatMessage } from "@/features/chat/types";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  clearAllTransactions,
  clearChatHistory,
  createTransaction,
  deleteTransaction,
  downloadBackup,
  fetchUserProfile,
  fetchUserTransactions,
  patchTransaction,
  persistChatMessage,
  restoreBackup,
  updateChatMessageTxStatus,
} from "./financial-data";

const apiRow = {
  id: "tx-1",
  type: "expense" as const,
  amount: 12,
  category: "food",
  description: null,
  transaction_date: "2026-05-15",
  status: "confirmed" as const,
  updated_at: "2026-05-15T10:00:00Z",
};

describe("financial-data", () => {
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
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(JSON.stringify([apiRow]), { status: 200 })),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetchUserTransactions maps API rows", async () => {
    const rows = await fetchUserTransactions();
    expect(rows).toHaveLength(1);
    expect(rows[0]?.amount).toBe(12);
    expect(rows[0]?.category).toBe("food");
    expect(rows[0]?.date).toBe("2026-05-15");
    expect(rows[0]?.confirmedAt).toBe("2026-05-15T10:00:00Z");
  });

  it("throws actionable error when actions are unavailable", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          error: { code: "ACTIONS_UNAVAILABLE", message: "run make dev" },
        }),
        { status: 503 },
      ),
    );
    await expect(fetchUserTransactions()).rejects.toThrow("run make dev");
  });

  it("falls back to status text for non-JSON errors", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response("upstream down", { status: 502 }));
    await expect(fetchUserTransactions()).rejects.toThrow("upstream down");
  });

  it("clearAllTransactions calls DELETE", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response("{}", { status: 200 }));
    await clearAllTransactions();
    expect(fetch).toHaveBeenCalledWith("/api/data/transactions", { method: "DELETE" });
  });

  it("fetchUserProfile applies defaults", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ display_name: "Quy" }), { status: 200 }),
    );
    const profile = await fetchUserProfile();
    expect(profile.display_name).toBe("Quy");
    expect(profile.currency).toBe("VND");
    expect(profile.locale).toBe("vi");
  });

  it("createTransaction posts payload and maps response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify(apiRow), { status: 200 }));
    const tx = await createTransaction({
      type: "expense",
      amount: 12,
      category: "food",
      transaction_date: "2026-05-15",
    });
    expect(tx.id).toBe("tx-1");
    expect(fetch).toHaveBeenCalledWith(
      "/api/data/transactions",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("patchTransaction sends PATCH to transaction id", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ ...apiRow, amount: 99 }), { status: 200 }),
    );
    const tx = await patchTransaction("tx-1", { amount: 99 });
    expect(tx.amount).toBe(99);
    expect(fetch).toHaveBeenCalledWith(
      "/api/data/transactions/tx-1",
      expect.objectContaining({ method: "PATCH" }),
    );
  });

  it("deleteTransaction sends DELETE to transaction id", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response("{}", { status: 200 }));
    await deleteTransaction("tx-1");
    expect(fetch).toHaveBeenCalledWith("/api/data/transactions/tx-1", { method: "DELETE" });
  });

  it("downloadBackup returns JSON blob", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response(JSON.stringify({ transactions: [apiRow] }), { status: 200 }),
    );
    const blob = await downloadBackup();
    expect(blob.type).toBe("application/json");
    const text = await blob.text();
    expect(text).toContain("tx-1");
  });

  it("restoreBackup posts parsed file contents", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response("{}", { status: 200 }));
    const file = new File([JSON.stringify({ transactions: [] })], "backup.json", {
      type: "application/json",
    });
    await restoreBackup(file);
    expect(fetch).toHaveBeenCalledWith(
      "/api/data/backup",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("persistChatMessage skips welcome id", async () => {
    const id = await persistChatMessage(
      {
        id: "welcome",
        role: "assistant",
        type: "text",
        content: "hi",
        timestamp: "t",
      },
      "user-1",
    );
    expect(id).toBeNull();
    expect(store.size).toBe(0);
  });

  it("persistChatMessage upserts chat history", async () => {
    const message: ChatMessage = {
      id: "m1",
      role: "user",
      type: "text",
      content: "hello",
      timestamp: "t",
    };
    await persistChatMessage(message, "user-1");
    const raw = store.get("finguard.chat.messages");
    expect(raw).toContain("hello");
  });

  it("updateChatMessageTxStatus updates stored message", async () => {
    const message: ChatMessage = {
      id: "m1",
      role: "assistant",
      type: "transaction",
      content: "pending",
      timestamp: "t",
      txStatus: "pending_confirmation",
    };
    store.set("finguard.chat.messages", JSON.stringify([message]));
    await updateChatMessageTxStatus("m1", "confirmed");
    const stored = JSON.parse(store.get("finguard.chat.messages") ?? "[]") as ChatMessage[];
    expect(stored[0]?.txStatus).toBe("confirmed");
  });

  it("clearChatHistory removes local messages", async () => {
    store.set("finguard.chat.messages", JSON.stringify([{ id: "m1" }]));
    await clearChatHistory();
    expect(store.has("finguard.chat.messages")).toBe(false);
  });
});
