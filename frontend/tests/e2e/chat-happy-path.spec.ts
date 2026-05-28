import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("sends expense and shows transaction card", async ({ page }) => {
  await waitForChatReady(page);
  const input = page.locator("textarea.chat-input");
  await input.fill("spent 12 on lunch");
  await page.locator("button.send-button").click();

  await expect(page.getByRole("button", { name: "Save Transaction" })).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.locator(".tx-amount")).toContainText("12.00");
});
