import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";
import { waitForChatReady } from "./helpers";

test("chat page has no critical a11y violations", async ({ page }) => {
  await waitForChatReady(page);

  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();

  const critical = results.violations.filter((v) => v.impact === "critical");
  expect(critical, JSON.stringify(critical, null, 2)).toHaveLength(0);
});
