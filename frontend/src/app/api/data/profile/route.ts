import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";

export async function GET() {
  const upstream = await proxyToActions("/data/profile");
  return mirrorActionsResponse(upstream);
}

export async function PATCH(request: Request) {
  const body = await request.text();
  const upstream = await proxyToActions("/data/profile", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body,
  });
  return mirrorActionsResponse(upstream);
}
