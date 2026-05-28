/** Upstream action server (FastAPI). Used only from Next.js route handlers. */
export function getActionsUrl(): string {
  return process.env.ACTIONS_URL?.trim() || "http://127.0.0.1:5055";
}

const ACTIONS_UNAVAILABLE = {
  error: {
    code: "ACTIONS_UNAVAILABLE",
    message: "Action server is not running. From the project root, run: make dev",
  },
} as const;

export async function proxyToActions(path: string, init?: RequestInit): Promise<Response> {
  const url = `${getActionsUrl()}${path}`;
  try {
    return await fetch(url, { ...init, cache: "no-store" });
  } catch {
    return Response.json(ACTIONS_UNAVAILABLE, { status: 503 });
  }
}

export async function mirrorActionsResponse(upstream: Response): Promise<Response> {
  const body = await upstream.text();
  const contentType = upstream.headers.get("content-type") ?? "application/json";
  return new Response(body, { status: upstream.status, headers: { "Content-Type": contentType } });
}
