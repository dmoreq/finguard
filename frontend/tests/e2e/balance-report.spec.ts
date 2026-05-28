import { expect, test } from "@playwright/test";
import { confirmPendingTransaction, waitForChatReady } from "./helpers";

test("dashboard reflects confirmed expense (CP-2)", async ({ page }) => {
  await waitForChatReady(page);
  await confirmPendingTransaction(page, "spent 12 on lunch");

  await expect(page.locator(".dashboard")).toBeVisible();
  await expect(page.locator(".dashboard")).toContainText("12");
});

test("balance question returns report in chat (CP-2)", async ({ page }) => {
  await waitForChatReady(page);
  await confirmPendingTransaction(page, "spent 12 on lunch");

  const input = page.locator("textarea.chat-input");
  await input.fill("what's my balance this month?");
  await page.locator("button.send-button").click();

  await expect(page.locator(".msg").last()).toContainText(/Thu:|Chi:|balance|Số dư/i, {
    timeout: 20_000,
  });
});
