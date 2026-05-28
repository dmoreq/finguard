import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("confirms pending transaction", async ({ page }) => {
  await waitForChatReady(page);
  const input = page.locator("textarea.chat-input");
  await input.fill("spent 20 on groceries");
  await page.locator("button.send-button").click();

  const save = page.getByRole("button", { name: "Save Transaction" });
  await expect(save).toBeVisible({ timeout: 20_000 });
  await save.click();

  await expect(page.getByText("Saved", { exact: false })).toBeVisible({ timeout: 20_000 });
});
