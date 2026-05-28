import { mapRasaWebhookToChatResponse } from "@/server/chat/map-rasa-responses";
import { checkChatRateLimit } from "@/server/chat/rate-limit";
import { getRasaUrl, resolveChatUserId } from "@/server/chat/resolve-user";
import { type RasaWebhookPayload, parseChatRequest } from "@/server/chat/schemas";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const json = await request.json();
    const { message } = parseChatRequest(json);
    const userId = await resolveChatUserId();

    const rate = checkChatRateLimit(userId);
    if (!rate.allowed) {
      return NextResponse.json(
        {
          error: {
            code: "RATE_LIMITED",
            message: `Too many messages. Try again in ${rate.retryAfterSec ?? 60} seconds.`,
          },
        },
        { status: 429 },
      );
    }

    const rasaUrl = getRasaUrl();
    if (!rasaUrl) {
      return NextResponse.json(
        {
          error: {
            code: "RASA_NOT_CONFIGURED",
            message: "Set RASA_URL in .env.local (e.g. http://localhost:5005).",
          },
        },
        { status: 503 },
      );
    }

    let rasaResponse: Response;
    try {
      rasaResponse = await fetch(`${rasaUrl}/webhooks/rest/webhook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender: userId,
          message,
          metadata: { user_id: userId },
        }),
        signal: AbortSignal.timeout(60_000),
      });
    } catch {
      return NextResponse.json(
        {
          error: {
            code: "RASA_UNAVAILABLE",
            message: "The assistant is not running. From the project root, run: make dev",
          },
        },
        { status: 503 },
      );
    }

    if (!rasaResponse.ok) {
      return NextResponse.json(
        {
          error: {
            code: "RASA_UNAVAILABLE",
            message: "The assistant is temporarily unavailable. Run make dev and try again.",
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
