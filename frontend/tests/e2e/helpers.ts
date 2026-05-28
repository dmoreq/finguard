import { expect, type Page } from "@playwright/test";

export async function waitForChatReady(page: Page): Promise<void> {
  await page.goto("/chat");
  await expect(page.locator("textarea.chat-input")).toBeVisible({ timeout: 30_000 });
}
