const WINDOW_MS = 60_000;
const MAX_REQUESTS = 60;

type Bucket = { count: number; resetAt: number };

const buckets = new Map<string, Bucket>();

/** In-process rate limit for hobby deploys; use Redis/Upstash at scale (SEC-6). */
export function checkChatRateLimit(userId: string): { allowed: boolean; retryAfterSec?: number } {
  const now = Date.now();
  const bucket = buckets.get(userId);

  if (!bucket || now >= bucket.resetAt) {
    buckets.set(userId, { count: 1, resetAt: now + WINDOW_MS });
    return { allowed: true };
  }

  if (bucket.count >= MAX_REQUESTS) {
    const retryAfterSec = Math.ceil((bucket.resetAt - now) / 1000);
    return { allowed: false, retryAfterSec };
  }

  bucket.count += 1;
  return { allowed: true };
}
