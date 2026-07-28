import { expect, test, type Page } from "@playwright/test";

// The homepage "Geboren op deze dag" block, against
// specs/birthday-today/birthday-today.cr.md.
//
// The block resolves the day in the visitor's own browser, so these tests drive it by
// moving the browser clock and timezone rather than by rebuilding the site.
//
// Fixture days, from the generated index:
//   9 March  — three entries; [R-2]'s confirmed worked example.
//   8 and 10 March — absent from the index, so both render the [R-4] empty state.
// 9 March sitting between two empty days is what makes the timezone tests below
// meaningful: reading the date in UTC instead of local time lands on an empty day.

const HEADING = "Geboren op deze dag";
const EMPTY_LINE = "Vandaag is er niemand uit deze stamboom geboren.";
const NO_JS_LINE =
  "Deze lijst wordt in je browser samengesteld. Zet JavaScript aan om te zien wie er vandaag geboren is.";

const NINTH_OF_MARCH = [
  { text: "Pieter Hoofman (1833-1874)", href: "/entity/i00013/" },
  { text: "Helena Louisa Walters (1873-1922)", href: "/entity/i00096/" },
  { text: "Anna Maria Christina Hoofman (1893-?)", href: "/entity/i00012/" },
];

async function openHomepageAt(page: Page, instant: string) {
  await page.clock.install({ time: new Date(instant) });
  await page.goto("/");
}

async function expectNinthOfMarch(page: Page) {
  const entries = page.locator("#birthday-block-content li");
  await expect(entries).toHaveCount(NINTH_OF_MARCH.length);
  for (const [position, entry] of NINTH_OF_MARCH.entries()) {
    await expect(entries.nth(position)).toHaveText(entry.text);
    await expect(entries.nth(position).locator("a")).toHaveAttribute(
      "href",
      entry.href,
    );
  }
}

test.describe("populated day", () => {
  test.use({ timezoneId: "Europe/Amsterdam" });

  test("[R-1][R-2] lists exactly the individuals recorded under that day", async ({
    page,
  }) => {
    await openHomepageAt(page, "2026-03-09T12:00:00+01:00");
    await expectNinthOfMarch(page);
  });

  test("[R-3] heading is 'Geboren op deze dag' and never says 'verjaardag'", async ({
    page,
  }) => {
    await openHomepageAt(page, "2026-03-09T12:00:00+01:00");

    const block = page.locator("#birthday-block");
    await expect(block.locator("h2")).toHaveText(HEADING);
    await expect(block).not.toContainText("verjaardag");
  });
});

test.describe("empty day", () => {
  test.use({ timezoneId: "Europe/Amsterdam" });

  test("[R-1][R-4] renders the empty-state line, block still in the DOM", async ({
    page,
  }) => {
    await openHomepageAt(page, "2026-03-10T12:00:00+01:00");

    const block = page.locator("#birthday-block");
    await expect(block).toBeVisible();
    await expect(page.locator("#birthday-block-content")).toHaveText(EMPTY_LINE);
    await expect(page.locator("#birthday-block-content li")).toHaveCount(0);
  });

  test("[R-3] the heading is there on an empty day too", async ({ page }) => {
    await openHomepageAt(page, "2026-03-10T12:00:00+01:00");

    const block = page.locator("#birthday-block");
    await expect(block.locator("h2")).toHaveText(HEADING);
    await expect(block).not.toContainText("verjaardag");
  });

  test("[R-4] a day emptied by the placeholder rule is empty, not missing", async ({
    page,
  }) => {
    // 1 January's only record was 'N.N. Walters', dropped by [R-10].
    await openHomepageAt(page, "2026-01-01T12:00:00+01:00");

    await expect(page.locator("#birthday-block")).toBeVisible();
    await expect(page.locator("#birthday-block-content")).toHaveText(EMPTY_LINE);
  });
});

test.describe("[R-1] the date is the visitor's local date, not UTC", () => {
  test.describe("ahead of UTC", () => {
    test.use({ timezoneId: "Pacific/Kiritimati" }); // UTC+14

    test("local 9 March while UTC is still 8 March", async ({ page }) => {
      // Locally 2026-03-09 02:00; in UTC still 2026-03-08, which is an empty day.
      await openHomepageAt(page, "2026-03-08T12:00:00Z");
      await expectNinthOfMarch(page);
    });
  });

  test.describe("behind UTC", () => {
    test.use({ timezoneId: "Pacific/Midway" }); // UTC-11

    test("local 9 March while UTC has moved to 10 March", async ({ page }) => {
      // Locally 2026-03-09 18:00; in UTC already 2026-03-10, which is an empty day.
      await openHomepageAt(page, "2026-03-10T05:00:00Z");
      await expectNinthOfMarch(page);
    });
  });
});

test.describe("[R-5] without JavaScript", () => {
  test.use({ javaScriptEnabled: false, timezoneId: "Europe/Amsterdam" });

  test("shows the static fallback message and no entries", async ({ page }) => {
    await page.goto("/");

    const block = page.locator("#birthday-block");
    await expect(block.locator("h2")).toHaveText(HEADING);
    await expect(page.locator("#birthday-block-content")).toHaveText(NO_JS_LINE);
    await expect(page.locator("#birthday-block-content li")).toHaveCount(0);
    await expect(block).not.toContainText("verjaardag");
  });
});
