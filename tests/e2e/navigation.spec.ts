import { expect, test } from "@playwright/test";

test("entity pages show breadcrumb context", async ({ page }) => {
  await page.goto("/entity/i00005/");

  await expect(page.getByRole("navigation", { name: "Breadcrumb" })).toContainText("Alles");
  await expect(page.getByRole("navigation", { name: "Breadcrumb" })).toContainText("Petrus Johannes Hoofman");
});

test("mobile menu keeps search reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
  await page.locator("#mobile-menu-button").click();
  await expect(page.locator('#mobile-menu a[href="/search"]')).toBeVisible();
});
