import { LOCAL_USER_ID } from "@/lib/constants";

/** Local dev user until authentication is added. */
export async function resolveChatUserId(): Promise<string> {
  return LOCAL_USER_ID;
}

/** Chat backend base URL (unified FastAPI on :5055). */
export function getChatBackendUrl(): string | null {
  const url = process.env.CHAT_BACKEND_URL?.trim() || process.env.RASA_URL?.trim();
  return url || null;
}

/** @deprecated Use getChatBackendUrl */
export function getRasaUrl(): string | null {
  return getChatBackendUrl();
}
