import { isLegacyAiParseEnabled } from "@/lib/env";
import { parseTransaction } from "@/server/ai/parse-transaction";
import { parseRequest } from "@/server/ai/schemas";
import { resolveChatUserId } from "@/server/chat/resolve-user";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  if (!isLegacyAiParseEnabled()) {
    return NextResponse.json(
      {
        error: {
          code: "DEPRECATED",
          message:
            "Direct AI parse is disabled. Use /api/chat with RASA_URL, or set ENABLE_LEGACY_AI_PARSE=true for development only.",
        },
      },
      { status: 410 },
    );
  }

  const userId = await resolveChatUserId();
  if (!userId) {
    return NextResponse.json(
      { error: { code: "UNAUTHORIZED", message: "Sign in required." } },
      { status: 401 },
    );
  }

  try {
    const json = await request.json();
    const input = parseRequest(json);
    const result = await parseTransaction(input);
    return NextResponse.json(result);
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("Invalid")) {
      return NextResponse.json({ error: error.message }, { status: 400 });
    }

    return NextResponse.json({ error: "Unable to parse message" }, { status: 500 });
  }
}
