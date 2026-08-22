import { expect, test } from "@playwright/test";

// The shared warm-archive design system, as computed values in light mode.
// These are the `archive` tokens from tailwind.config.cjs and the shared
// font stacks; every primary route must resolve to the same values.
const archiveCanvas = "rgb(243, 236, 226)"; // archive.canvas #f3ece2
const archiveInk = "rgb(47, 36, 29)"; // archive.ink #2f241d
const bodyFontStack = '"IBM Plex Sans", "Segoe UI", sans-serif';
const displayFontStack = '"Iowan Old Style", "Palatino Linotype", serif';

const routes = [
  { label: "home", path: "/" },
  { label: "search", path: "/search" },
  { label: "entity browse", path: "/entity" },
  { label: "entity detail", path: "/entity/i00005/" },
];

for (const route of routes) {
  test(`${route.label} route uses the shared archive palette and typography`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: "light" });
    await page.goto(route.path);

    // The page shell comes from the shared utility layer, not per-page styling.
    await expect(page.locator("body")).toHaveClass(/page-shell/);

    const computed = await page.evaluate(() => {
      const body = getComputedStyle(document.body);
      const heading = document.querySelector("h1, h2");
      return {
        background: body.backgroundColor,
        textColor: body.color,
        bodyFont: body.fontFamily,
        headingFont: heading ? getComputedStyle(heading).fontFamily : null,
      };
    });

    expect(computed.background).toBe(archiveCanvas);
    expect(computed.textColor).toBe(archiveInk);
    expect(computed.bodyFont).toBe(bodyFontStack);
    expect(computed.headingFont).toBe(displayFontStack);
  });
}
