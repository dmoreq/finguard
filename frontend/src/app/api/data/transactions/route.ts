import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";

export async function GET() {
  const upstream = await proxyToActions("/data/transactions");
  return mirrorActionsResponse(upstream);
}

export async function DELETE() {
  const upstream = await proxyToActions("/data/transactions", { method: "DELETE" });
  return mirrorActionsResponse(upstream);
}
