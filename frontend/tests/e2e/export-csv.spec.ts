import { expect, test } from "@playwright/test";

test("export returns CSV with header row", async ({ request }) => {
  const response = await request.get("/api/transactions/export");
  expect(response.ok()).toBeTruthy();
  const contentType = response.headers()["content-type"] ?? "";
  expect(contentType).toContain("text/csv");
  const body = await response.text();
  expect(body.split("\n")[0]).toMatch(/date|amount|category/i);
});
