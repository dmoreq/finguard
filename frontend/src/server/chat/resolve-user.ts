/**
 * Resolves the user id for Rasa sender_id + metadata.
 * Uses FIN_GUARD_DEV_USER_ID until Supabase auth is wired on the frontend.
 */
export function resolveChatUserId(): string | null {
  const devUser = process.env.FIN_GUARD_DEV_USER_ID?.trim();
  if (devUser) return devUser;
  return null;
}

export function getRasaUrl(): string | null {
  const url = process.env.RASA_URL?.trim();
  return url || null;
}
