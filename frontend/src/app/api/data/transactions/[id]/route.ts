import { mirrorActionsResponse, proxyToActions } from "@/server/actions/proxy";

type Params = { params: Promise<{ id: string }> };

export async function PATCH(request: Request, { params }: Params) {
  const { id } = await params;
  const body = await request.text();
  const upstream = await proxyToActions(`/data/transactions/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body,
  });
  return mirrorActionsResponse(upstream);
}

export async function DELETE(_request: Request, { params }: Params) {
  const { id } = await params;
  const upstream = await proxyToActions(`/data/transactions/${id}`, { method: "DELETE" });
  return mirrorActionsResponse(upstream);
}
