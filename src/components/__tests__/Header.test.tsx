import { describe, expect, it } from "vitest";

import {
  initialMobileMenuExpanded,
  nextMobileMenuExpanded,
  normalizeBreadcrumbs,
} from "../headerState";

describe("Header", () => {
  it("normalizes breadcrumb context without dropping valid items", () => {
    const crumbs = normalizeBreadcrumbs([
      { label: "Home", href: "/" },
      { label: "  " },
      { label: "Alles", href: "/entity" },
      { label: "Petrus Johannes Hoofman" },
    ]);

    expect(crumbs).toEqual([
      { label: "Home", href: "/" },
      { label: "Alles", href: "/entity" },
      { label: "Petrus Johannes Hoofman" },
    ]);
  });

  it("toggles the mobile menu state from the collapsed default", () => {
    expect(initialMobileMenuExpanded).toBe(false);
    expect(nextMobileMenuExpanded(initialMobileMenuExpanded)).toBe(true);
    expect(nextMobileMenuExpanded(true)).toBe(false);
  });
});
