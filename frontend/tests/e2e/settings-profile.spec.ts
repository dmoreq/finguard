import { expect, test } from "@playwright/test";

test("saves profile settings", async ({ page }) => {
  await page.goto("/settings");
  await expect(page.getByRole("heading", { name: "Profile settings" })).toBeVisible();

  await page.locator("#currency").selectOption("EUR");
  await page.getByRole("button", { name: "Save" }).click();

  await expect(page.getByText("Settings saved.")).toBeVisible({ timeout: 20_000 });
});
