export function hasSupabaseConfig() {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  );
}

export function hasAiConfig() {
  return Boolean(process.env.OPENAI_API_KEY);
}

export function hasRasaConfig() {
  return Boolean(process.env.RASA_URL?.trim());
}

export function hasChatConfig() {
  return hasRasaConfig() || hasAiConfig();
}
