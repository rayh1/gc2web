import { expect, test } from "@playwright/test";

test("sparse entity page renders intentionally with empty groups omitted", async ({ page }) => {
  await page.goto("/entity/s00001/");

  await expect(page.getByRole("heading", { name: /Police Reports 1940-1945/i })).toBeVisible();
  // No optional metadata: the lifespan tile and the section nav are omitted,
  // not rendered empty.
  await expect(page.getByText("Levensloop")).toHaveCount(0);
  await expect(page.getByRole("navigation", { name: "Secties" })).toHaveCount(0);
  await expect(page.getByText("0 hoofdsecties")).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Breadcrumb" })).toBeVisible();
});

test("dense entity page surfaces grouped overview content", async ({ page }) => {
  await page.goto("/entity/i00005/");

  await expect(page.getByText(/Familietak Hoofman/i)).toBeVisible();
  await expect(page.getByText(/Levensloop/i)).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Secties" })).toContainText("Gegevens");
  await expect(page.getByRole("heading", { name: "Gegevens" })).toBeVisible();
});
