import { expect, test } from "@playwright/test";

test("entity page surfaces grouped overview content", async ({ page }) => {
  await page.goto("/entity/i00005/");

  await expect(page.getByText(/Familietak Hoofman/i)).toBeVisible();
  await expect(page.getByText(/Levensloop/i)).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Secties" })).toContainText("Gegevens");
  await expect(page.getByRole("heading", { name: "Gegevens" })).toBeVisible();
});
