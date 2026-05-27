import { fallbackParse } from "./fallback-parser";
import { type AiParseResult, type ParseRequest, parseAiResult } from "./schemas";

export async function parseTransaction(input: ParseRequest): Promise<AiParseResult> {
  if (!process.env.OPENAI_API_KEY) {
    return fallbackParse(input);
  }

  const result = await callOpenAI(input);
  return parseAiResult(result);
}

async function callOpenAI(input: ParseRequest) {
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: process.env.AI_MODEL || "gpt-4.1-mini",
      input: [
        {
          role: "system",
          content:
            "You are Finguard, an AI financial assistant. Extract transactions or report intents from user messages. Return only data matching the JSON schema. Never create a confirmed transaction; all transactions must be pending_confirmation.",
        },
        {
          role: "user",
          content: JSON.stringify({
            today: input.today,
            message: input.message,
            recentTransactions: input.transactions.slice(-12),
          }),
        },
      ],
      text: {
        format: {
          type: "json_schema",
          name: "finguard_parse_result",
          strict: true,
          schema: {
            type: "object",
            additionalProperties: false,
            properties: {
              intent: { type: "string", enum: ["transaction", "report", "conversation"] },
              message: { type: "string" },
              transaction: {
                anyOf: [
                  { type: "null" },
                  {
                    type: "object",
                    additionalProperties: false,
                    properties: {
                      id: { type: "string" },
                      type: { type: "string", enum: ["income", "expense", "pending"] },
                      amount: { type: "number", exclusiveMinimum: 0 },
                      category: { type: "string" },
                      description: { anyOf: [{ type: "string" }, { type: "null" }] },
                      date: { type: "string", pattern: "^\\d{4}-\\d{2}-\\d{2}$" },
                      status: { type: "string", enum: ["pending_confirmation"] },
                      aiConfidence: { type: "number", minimum: 0, maximum: 1 },
                    },
                    required: [
                      "id",
                      "type",
                      "amount",
                      "category",
                      "description",
                      "date",
                      "status",
                      "aiConfidence",
                    ],
                  },
                ],
              },
            },
            required: ["intent", "message", "transaction"],
          },
        },
      },
    }),
  });

  if (!response.ok) {
    return fallbackParse(input);
  }

  const payload = (await response.json()) as { output_text?: string };
  if (!payload.output_text) return fallbackParse(input);

  return JSON.parse(payload.output_text);
}
