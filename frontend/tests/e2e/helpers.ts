import { expect, type Page } from "@playwright/test";

export async function waitForChatReady(page: Page): Promise<void> {
  await page.goto("/chat");
  await expect(page.locator("textarea.chat-input")).toBeVisible({ timeout: 30_000 });
}

export async function resetFinancialData(page: Page): Promise<void> {
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Clear txs" }).click();
  await page.getByRole("button", { name: "Clear chat" }).click();
}

export async function confirmPendingTransaction(page: Page, message: string): Promise<void> {
  const input = page.locator("textarea.chat-input");
  await input.fill(message);
  await page.locator("button.send-button").click();

  const save = page.getByRole("button", { name: "Save Transaction" });
  await expect(save).toBeVisible({ timeout: 20_000 });
  await save.click();
  await expect(page.getByText("Saved", { exact: false })).toBeVisible({ timeout: 20_000 });
}
