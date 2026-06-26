import { expect, test } from "@playwright/test";

test("homepage exposes archive purpose and primary actions", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: /een warme ingang/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /zoeken in personen en bronnen/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /alles bekijken/i })).toBeVisible();
  await expect(page.getByRole("heading", { name: /begin bij een familietak/i })).toBeVisible();
});
