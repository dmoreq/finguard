import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("records income and shows pending card", async ({ page }) => {
  await waitForChatReady(page);
  const input = page.locator("textarea.chat-input");
  await input.fill("freelance payment 500 dollars");
  await page.locator("button.send-button").click();

  await expect(page.getByRole("button", { name: "Save Transaction" })).toBeVisible({
    timeout: 20_000,
  });
  await expect(page.locator(".tx-amount")).toContainText("500.00");
  await expect(page.locator(".badge")).toContainText("Income");
});
