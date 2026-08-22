import { expect, test, type Page } from "@playwright/test";

// One long page per layout: the entity index uses PageLayout, a dense
// person page uses BlogPostLayout. The control ships via the shared
// Footer, so it must behave identically on both.
const longPages = [
  { label: "entity index (PageLayout)", path: "/entity" },
  { label: "person page (BlogPostLayout)", path: "/entity/i00005/" },
];

const VIEWPORT = { width: 1280, height: 720 };

const control = (page: Page) =>
  page.getByRole("button", { name: "Terug naar boven", exact: true });

async function scrollTo(page: Page, y: number) {
  await page.evaluate(
    (top) => window.scrollTo({ top, behavior: "instant" }),
    y,
  );
  await page.waitForFunction((top) => window.scrollY >= top, y);
}

test("back-to-top control appears in the lower-right after scrolling down", async ({ page }) => {
  for (const { label, path } of longPages) {
    await page.setViewportSize(VIEWPORT);
    await page.goto(path);
    await scrollTo(page, 600);

    const button = control(page);
    await expect(button, `${label}: control visible after 600px scroll`).toBeVisible();

    const box = await button.boundingBox();
    expect(box, `${label}: control has a bounding box`).not.toBeNull();
    // Lower-right quadrant of the viewport (boundingBox is in viewport
    // coordinates for a position:fixed element).
    expect(box!.x, `${label}: control in right half`).toBeGreaterThan(VIEWPORT.width / 2);
    expect(box!.y, `${label}: control in lower half`).toBeGreaterThan(VIEWPORT.height / 2);
    expect(box!.x + box!.width, `${label}: control inside viewport (x)`).toBeLessThanOrEqual(VIEWPORT.width);
    expect(box!.y + box!.height, `${label}: control inside viewport (y)`).toBeLessThanOrEqual(VIEWPORT.height);

    const fixed = await button.evaluate((el) => getComputedStyle(el).position);
    expect(fixed, `${label}: control is fixed`).toBe("fixed");
  }
});

test("back-to-top control stays hidden while the page is at the top", async ({ page }) => {
  for (const { label, path } of longPages) {
    await page.setViewportSize(VIEWPORT);
    await page.goto(path);
    expect(await page.evaluate(() => window.scrollY), `${label}: page starts at top`).toBe(0);

    // A visibility-hidden element leaves the accessibility tree, so
    // address it directly rather than by role.
    const button = page.locator('button[aria-label="Terug naar boven"]');
    await expect(button, `${label}: control hidden at top`).toBeHidden();
    const pointerEvents = await button.evaluate((el) => getComputedStyle(el).pointerEvents);
    expect(pointerEvents, `${label}: control takes no pointer events`).toBe("none");
  }
});

test("back-to-top control scrolls the page back to the very top", async ({ page }) => {
  for (const { label, path } of longPages) {
    await page.setViewportSize(VIEWPORT);
    await page.goto(path);
    await scrollTo(page, 600);

    await control(page).click();
    // Smooth scrolling animates, so poll until it settles at 0.
    await page.waitForFunction(() => window.scrollY === 0, undefined, { timeout: 5000 });
    expect(await page.evaluate(() => window.scrollY), `${label}: scrollY back to 0`).toBe(0);
  }
});

test("back-to-top control carries the exact Dutch accessible name", async ({ page }) => {
  for (const { label, path } of longPages) {
    await page.setViewportSize(VIEWPORT);
    await page.goto(path);
    await scrollTo(page, 600);

    const button = control(page);
    await expect(button, `${label}: exactly one control by role+name`).toHaveCount(1);
    await expect(button, `${label}: control visible`).toBeVisible();
    const tag = await button.evaluate((el) => el.tagName.toLowerCase());
    expect(["button", "a"], `${label}: real button or link`).toContain(tag);
  }
});
