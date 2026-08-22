---
slug: back-to-top
source: inline-cr
---

# Back-to-top control

## 1. Intent

Long pages (entity indexes, birthday lists, ascii-tree pages) currently offer no way back to
the navigation except manual scrolling. Add a small, theme-consistent back-to-top control that
appears once the reader has scrolled down and returns them to the top of the page. Second
real-effort acceptance target for the cr4 v0.2 test-bound-gates revision, chosen small and
visual on purpose.
<!-- observed: tests/e2e/ 2026-08-22 — no scroll-return affordance asserted anywhere; src/components/ has no such component -->

## 2. Functional requirements

[R-1] On every page, once the viewport has scrolled down at least 300 CSS pixels, a
back-to-top control is visible, fixed near the lower-right corner of the viewport.
<!-- from CR:intent -->
- AC: an e2e test scrolls a long page to ≥ 600px at a desktop viewport and asserts the control
  is visible and positioned in the lower-right quadrant of the viewport.

[R-2] While the page is at the top (scroll position under the 300px threshold), the control is
not visible and takes no pointer events. <!-- from CR:intent -->
- AC: an e2e test at scroll position 0 asserts the control is not visible.

[R-3] Activating the control returns the viewport to the top of the page
(`window.scrollY` reaches 0). <!-- from CR:intent -->
- AC: an e2e test scrolls down, activates the control, and asserts the final scroll position
  is 0.

[R-4] The control is a real button or link whose accessible name is exactly
`Terug naar boven`. <!-- from CR:intent -->
- AC: an e2e test locates the control by role with accessible name `Terug naar boven`.

## 3. Technical constraints and decisions

- **Locked:** no new npm dependencies. <!-- from CR:intent -->
- **Locked:** the visible/accessible label text is Dutch: `Terug naar boven` (the site's UI
  language). <!-- observed: tests/e2e/homepage.spec.ts asserts Dutch headings and link names -->
- **Delegated:** exact placement in the shared shell (Footer vs layouts), icon vs text
  rendering, smooth vs instant scroll, and how the 300px threshold is implemented — as long as
  the [R-n] criteria hold on both layouts. <!-- from CR:intent -->

## 4. Invariants

[I-1] Every color in code added for this feature comes from the archive palette tokens: added
lines introduce no raw hex colors and no non-archive Tailwind color utilities.
<!-- observed: specs/website-beauty review 2026-08-22 — the effort's only real code defect was an off-palette CTA; this invariant is that lesson, stated for new code -->

## 5. Scope fence

- No changes to the header, theme toggle, or search components. <!-- from CR:intent -->
- No changes under gen_site/ and no changes to GEDCOM data. <!-- from CR:intent -->
- No visual-QA machinery; ordinary review judgment only. <!-- from CR:intent -->
