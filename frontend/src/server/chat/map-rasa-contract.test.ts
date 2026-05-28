import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { mapRasaWebhookToChatResponse } from "./map-rasa-responses";
import type { RasaWebhookPayload } from "./schemas";

const fixturesDir = join(dirname(fileURLToPath(import.meta.url)), "fixtures");

function loadFixture(name: string): RasaWebhookPayload[] {
  return JSON.parse(readFileSync(join(fixturesDir, name), "utf8")) as RasaWebhookPayload[];
}

describe("Rasa webhook golden fixtures", () => {
  it("maps balance fixture to report with reportData", () => {
    const result = mapRasaWebhookToChatResponse(loadFixture("balance-webhook.json"));
    expect(result.messages[0]?.type).toBe("report");
    if (result.messages[0]?.type === "report") {
      expect(result.messages[0].reportData?.totalIncome).toBe(3200);
      expect(result.messages[0].reportData?.net).toBe(2750);
    }
  });

  it("maps spending fixture to report with top category", () => {
    const result = mapRasaWebhookToChatResponse(loadFixture("spending-webhook.json"));
    expect(result.messages[0]?.type).toBe("report");
    if (result.messages[0]?.type === "report") {
      expect(result.messages[0].reportData?.totalExpenses).toBe(200);
      expect(result.messages[0].reportData?.topCategory).toBe("Food");
    }
  });

  it("maps transaction-pending golden fixture", () => {
    const result = mapRasaWebhookToChatResponse(loadFixture("transaction-pending-webhook.json"));
    expect(result.messages[0]?.type).toBe("transaction");
    if (result.messages[0]?.type === "transaction") {
      expect(result.messages[0].transaction.amount).toBe(18);
      expect(result.messages[0].transaction.category).toBe("dining");
    }
  });

  it("maps text-only golden fixture", () => {
    const result = mapRasaWebhookToChatResponse(loadFixture("text-only-webhook.json"));
    expect(result.messages[0]?.type).toBe("text");
    expect(result.messages[0]?.content).toContain("log expenses");
  });

  it("falls back when custom transaction payload is invalid", () => {
    const result = mapRasaWebhookToChatResponse(loadFixture("invalid-payload-webhook.json"));
    expect(result.messages[0]?.type).toBe("text");
    expect(result.messages[0]?.content).toContain("help");
  });
});
