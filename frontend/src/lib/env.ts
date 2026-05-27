export function hasSupabaseConfig() {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  );
}

export function isLegacyAiParseEnabled() {
  return process.env.ENABLE_LEGACY_AI_PARSE === "true";
}

export function isDevUserFallbackEnabled() {
  return process.env.ENABLE_DEV_USER_FALLBACK === "true";
}

export function hasRasaConfig() {
  return Boolean(process.env.RASA_URL?.trim());
}

export function hasChatConfig() {
  return hasRasaConfig() && (hasSupabaseConfig() || isDevUserFallbackEnabled());
}
