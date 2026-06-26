import { expect, test } from "@playwright/test";

test("search finds contextual matches from metadata", async ({ page }) => {
  await page.goto("/search");

  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.locator("#search").fill("Wilhelmina");
  await page.waitForTimeout(500);
  await expect(page.getByText(/Partner van Wilhelmina Johanna Voorbraak/i)).toBeVisible();
});
