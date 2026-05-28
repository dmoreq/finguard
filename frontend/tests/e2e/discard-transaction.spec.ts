import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("discards pending transaction", async ({ page }) => {
  await waitForChatReady(page);
  const input = page.locator("textarea.chat-input");
  await input.fill("spent 8 on snacks");
  await page.locator("button.send-button").click();

  await expect(page.getByRole("button", { name: "Discard" })).toBeVisible({ timeout: 20_000 });
  await page.getByRole("button", { name: "Discard" }).click();

  await expect(page.getByText("Discarded")).toBeVisible({ timeout: 20_000 });
});
