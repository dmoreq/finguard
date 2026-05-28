import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";

export async function GET() {
  const upstream = await proxyToActions("/data/backup");
  return mirrorActionsResponse(upstream);
}

export async function POST(request: Request) {
  const body = await request.text();
  const upstream = await proxyToActions("/data/restore", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  return mirrorActionsResponse(upstream);
}
