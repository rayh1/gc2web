# Review — back-to-top (pass 2)

Delta: baseline `d6f01f9e1469` (the ref the gate set pins; spec carries no code0_ref, tip =
dirty working tree, identity `WORKING-TREE:3886e00d6749`). Repo root `/workspace/gc2web`.
Code files: `src/components/BackToTop.astro` (new), `src/components/Footer.astro` (+2 lines),
`tests/e2e/back-to-top.spec.ts` (new). The pre-existing uncommitted edit to
`specs/birthday-today/birthday-today.cr.md` is not part of this delta (spec artifact of another
effort, untouched).

## Elements

- [R-1] satisfied — `BackToTop.astro:36` (`const show = window.scrollY >= THRESHOLD;`,
  THRESHOLD=300 at `:32`) toggles the shown/hidden class sets (`:37-38`) on a
  `fixed bottom-6 right-6` button (`:11`); rendered on every page via `Footer.astro:17`, and
  Footer sits in both layouts. Test `back-to-top control appears in the lower-right after
  scrolling down` asserts visibility, lower-right quadrant, and `position: fixed` on BOTH
  layouts.
- [R-2] satisfied — initial classes `invisible opacity-0 pointer-events-none` (`:11`) plus the
  initial `update()` call (`:41`); test `…stays hidden while the page is at the top` asserts
  hidden AND `pointer-events: none` at scrollY 0 on both layouts.
- [R-3] satisfied — click listener `:42-44` runs `window.scrollTo({ top: 0, … })`; test
  `…scrolls the page back to the very top` polls until `scrollY === 0`.
- [R-4] satisfied — `aria-label="Terug naar boven"` (`:10`) on a real `<button>`, SVG child
  `aria-hidden`; test `…carries the exact Dutch accessible name` locates by role with
  `exact: true` and count 1.
- [I-1] satisfied — every color utility in the added code is an `archive-*` token; SVG uses
  `currentColor`; `shadow-lg`/`z-50` are not color utilities. E1's grep run: `palette-clean`.

Untagged-obligation lint: 0 hits outside tagged elements. Locked "no new npm dependencies":
E2 green (package files byte-identical). Locked Dutch label: covered by T4's exact-name test.
Scope fence: E3 green (header/toggle/search/gen_site byte-identical); no visual-QA machinery
added.

## Lanes

Reviewer's own pass: `verify.py --project . --json --tests "npm run test:unit"
--tests "npm run test:e2e"` → verdict `clean` (both suites exit 0; constitution lane clean,
C-1 PASS). This is the suite declaration the website-beauty review established for this repo.
The builder additionally ran the gen_site pytest suite: 53 passed, 4 failed, 1 error — ALL
pre-existing at baseline: the delta contains no Python and `git diff d6f01f9e1469 -- gen_site`
is empty (E3), so those failures reproduce identically at baseline; they are the known
Hoofman.ged data-drift item (Friethoff ingest) plus a missing external fixture path. Recorded,
not findings; not part of this repo's established verify suite.

## Pass audit

Pass-verdict spot-check: 4/4 re-read by verifier subagent, 0 overturned (R-1, R-3, R-4, I-1;
no high-stakes class in this delta; sample exceeds max(3, 20%)). All entries carried
`read_line` proof; the I-1 audit independently swept the SVG and Footer lines for colors.

## Gate-set audit (J pass)

Coverage: T1→[R-1], T2→[R-2], T3→[R-3], T4→[R-4], E1→[I-1], E2→Locked-deps,
E3→both checkable fence bullets; waivers: Dutch-label lock `covered-by:T4` (the exact-name
test IS the check), visual-QA fence bullet `review-only` — both sound.

Bindings (DEMAND vs test, quoted in § Elements above): T1–T4 all **faithful** — each test runs
in a real browser, on both layouts, and asserts exactly what its DEMAND pins (T1 even adds the
in-viewport and position:fixed checks; T2 covers the pointer-events half of R-2's wording).
BOUND written for all four via the [GATE] banking path.

Finding [F-1] (E1, wrong-boundary): as derived, E1's `git diff <ref> -- src` never shows an
UNTRACKED file's content, so on a feature made of new files the palette grep is vacuously
clean unless `git add -N` happens to be set (the builder set it manually and reported doing
so). The gate must not depend on transient index state — repair: E1's CHECK prepends
`git add -N src` itself. Routed as [GATE] task #5, repaired (CHECK now prepends `git add -N src` itself), banked under the open task at the pass-1 checker run, and re-evaluated green; closed this pass. NEVER-RED discharge unchanged.

RED-AT-BASELINE: not opted into on this effort (greenfield tests; derivation note in the gate
file) — concurred.

Build cross-check: reconcile result appended after the checker runs.

review status: {"findings_open": 0, "spec_findings": 0, "code_findings": 0}
review reduced: {"reduced": false, "reason": ""}
review element: {"id": "R-1", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-2", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-3", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "R-4", "kind": "requirement", "verdict": "satisfied", "findings": ""}
review element: {"id": "I-1", "kind": "invariant", "verdict": "satisfied", "findings": ""}

reconcile: clean — run after convergence; review directly follows the build.
