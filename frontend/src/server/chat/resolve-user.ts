import { hasSupabaseConfig } from "@/lib/env";
import { createServerSupabaseClient } from "@/lib/supabase/server";

/** Authenticated user id for Rasa sender_id and metadata. */
export async function resolveChatUserId(): Promise<string | null> {
  if (!hasSupabaseConfig()) return null;

  const supabase = await createServerSupabaseClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return user?.id ?? null;
}

export function getRasaUrl(): string | null {
  const url = process.env.RASA_URL?.trim();
  return url || null;
}
