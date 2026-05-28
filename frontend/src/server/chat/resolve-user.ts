import { LOCAL_USER_ID } from "@/lib/constants";

/** Local dev user until authentication is added. */
export async function resolveChatUserId(): Promise<string> {
  return LOCAL_USER_ID;
}

export function getRasaUrl(): string | null {
  const url = process.env.RASA_URL?.trim();
  return url || null;
}
