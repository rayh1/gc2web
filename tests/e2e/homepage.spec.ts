import { expect, test } from "@playwright/test";

const viewports = [
  { label: "desktop", width: 1280, height: 720 },
  { label: "mobile", width: 375, height: 667 },
];

for (const viewport of viewports) {
  test(`homepage shows purpose and both primary actions in the first ${viewport.label} viewport`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height });
    await page.goto("/");

    const heading = page.getByRole("heading", { level: 1, name: "Mijn voorouders" });
    const purpose = page.getByText(/Verken personen, bronnen en familieverbanden/);
    const searchAction = page.getByRole("link", { name: /zoeken in personen en bronnen/i });
    const browseAction = page.getByRole("link", { name: /alles bekijken/i });

    // First view: no scrolling has happened, and purpose text plus both
    // primary actions sit inside the initial viewport.
    expect(await page.evaluate(() => window.scrollY)).toBe(0);
    await expect(heading).toBeInViewport({ ratio: 0.95 });
    await expect(purpose).toBeInViewport({ ratio: 0.95 });
    await expect(searchAction).toBeInViewport({ ratio: 0.95 });
    await expect(browseAction).toBeInViewport({ ratio: 0.95 });

    await expect(searchAction).toHaveAttribute("href", "/search");
    await expect(browseAction).toHaveAttribute("href", "/entity");
  });
}

test("homepage keeps the family-branch entry points reachable", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /begin bij een familietak/i })).toBeVisible();
  await expect(page.locator('a[href="/entity/i00005/"]').first()).toBeVisible();
  await expect(page.locator('a[href="/entity/i00073/"]').first()).toBeVisible();
});
