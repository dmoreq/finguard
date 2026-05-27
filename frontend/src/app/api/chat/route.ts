import { todayISO } from "@/lib/format";
import { parseTransaction } from "@/server/ai/parse-transaction";
import { parseRequest } from "@/server/ai/schemas";
import {
  mapParseResultToChatResponse,
  mapRasaWebhookToChatResponse,
} from "@/server/chat/map-rasa-responses";
import { getRasaUrl, resolveChatUserId } from "@/server/chat/resolve-user";
import { type RasaWebhookPayload, parseChatRequest } from "@/server/chat/schemas";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const json = await request.json();
    const { message } = parseChatRequest(json);
    const userId = resolveChatUserId();

    if (!userId) {
      return NextResponse.json(
        {
          error: {
            code: "UNAUTHORIZED",
            message:
              "Chat requires a user id. Set FIN_GUARD_DEV_USER_ID in .env.local for local development.",
          },
        },
        { status: 401 },
      );
    }

    const rasaUrl = getRasaUrl();
    if (!rasaUrl) {
      return fallbackParse(message);
    }

    const rasaResponse = await fetch(`${rasaUrl}/webhooks/rest/webhook`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sender: userId,
        message,
        metadata: { user_id: userId },
      }),
      signal: AbortSignal.timeout(60_000),
    });

    if (!rasaResponse.ok) {
      return NextResponse.json(
        {
          error: {
            code: "RASA_UNAVAILABLE",
            message: "Chat service is temporarily unavailable.",
          },
        },
        { status: 503 },
      );
    }

    const payload = (await rasaResponse.json()) as RasaWebhookPayload[];
    const result = mapRasaWebhookToChatResponse(payload);
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Invalid")) {
      return NextResponse.json(
        { error: { code: "VALIDATION_ERROR", message: error.message } },
        { status: 400 },
      );
    }

    return NextResponse.json(
      { error: { code: "INTERNAL_ERROR", message: "Unable to process message." } },
      { status: 500 },
    );
  }
}

async function fallbackParse(message: string) {
  try {
    const input = parseRequest({
      message,
      today: todayISO(),
      transactions: [],
    });
    const result = await parseTransaction(input);
    return NextResponse.json(mapParseResultToChatResponse(result));
  } catch {
    return NextResponse.json(
      {
        error: {
          code: "PARSE_UNAVAILABLE",
          message: "Set RASA_URL or OPENAI_API_KEY to enable chat.",
        },
      },
      { status: 503 },
    );
  }
}
