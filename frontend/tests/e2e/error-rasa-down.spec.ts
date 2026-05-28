import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("shows error bubble when chat API fails", async ({ page }) => {
  await page.route("**/api/chat", (route) => route.abort("failed"));
  await waitForChatReady(page);
  const input = page.locator("textarea.chat-input");
  await input.fill("spent 5 on tea");
  await page.locator("button.send-button").click();

  await expect(page.getByText(/trouble with that/i)).toBeVisible({ timeout: 15_000 });
});
