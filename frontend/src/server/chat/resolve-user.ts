import { hasSupabaseConfig, isDevUserFallbackEnabled } from "@/lib/env";
import { createServerSupabaseClient } from "@/lib/supabase/server";

/**
 * Resolves the user id for Rasa sender_id + metadata.
 * Prefers Supabase Auth session; optional dev uuid when ENABLE_DEV_USER_FALLBACK=true.
 */
export async function resolveChatUserId(): Promise<string | null> {
  if (hasSupabaseConfig()) {
    try {
      const supabase = await createServerSupabaseClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user?.id) return user.id;
    } catch {
      // Misconfigured env — fall through to dev fallback if allowed
    }
  }

  if (isDevUserFallbackEnabled()) {
    const devUser = process.env.FIN_GUARD_DEV_USER_ID?.trim();
    if (devUser) return devUser;
  }

  return null;
}

export function getRasaUrl(): string | null {
  const url = process.env.RASA_URL?.trim();
  return url || null;
}
