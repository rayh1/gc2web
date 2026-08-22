import { expect, test } from "@playwright/test";

const pageTypes = [
  { label: "browse", path: "/entity", crumb: "Alles" },
  { label: "search", path: "/search", crumb: "Zoeken" },
  { label: "entity", path: "/entity/i00005/", crumb: "Petrus Johannes Hoofman" },
];

const viewports = [
  { label: "desktop", width: 1280, height: 720 },
  { label: "mobile", width: 375, height: 667 },
];

for (const viewport of viewports) {
  for (const pageType of pageTypes) {
    test(`${pageType.label} page keeps home and search reachable with breadcrumb context (${viewport.label})`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto(pageType.path);

      const breadcrumb = page.getByRole("navigation", { name: "Breadcrumb" });
      await expect(breadcrumb).toBeVisible();
      await expect(breadcrumb).toContainText(pageType.crumb);
      // Home stays reachable from the breadcrumb trail.
      await expect(breadcrumb.locator('a[href="/"]')).toBeVisible();

      if (viewport.label === "desktop") {
        await expect(page.locator('header nav a[href="/search"]').first()).toBeVisible();
      } else {
        await page.waitForLoadState("networkidle");
        await page.locator("#mobile-menu-button").click();
        await expect(page.locator('#mobile-menu a[href="/search"]')).toBeVisible();
      }
    });
  }
}

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
