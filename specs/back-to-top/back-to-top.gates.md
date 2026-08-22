Derived-from: specs/back-to-top/back-to-top.cr.md
Spec-sha: 18a2dfa8b8c9
Test-runner: npx playwright test {path} -g {name}
Build: npm run build

Derivation note: RED-AT-BASELINE deliberately not opted into — the feature and its tests are
greenfield, so a baseline run could only go red on test-file absence (the weak-proof case
recorded in the tally-csv stage), and each opt-in costs a full site build.

- [x] T1 visible-after-scroll
  DEMAND: prove in a real browser that a long page scrolled at least 600px shows the control visible and fixed in the lower-right quadrant of the viewport
  SOURCE: "[R-1] On every page, once the viewport has scrolled down at least 300 CSS pixels, a back-to-top control is visible, fixed near the lower-right corner of the viewport."
  BOUND: tests/e2e/back-to-top.spec.ts::back-to-top control appears in the lower-right after scrolling down
  EXPECT: test-passes
  EVIDENCE: test-passes: 1 bound test(s) exit=0

- [x] T2 hidden-at-top
  DEMAND: prove in a real browser that at scroll position 0 the control is not visible
  SOURCE: "[R-2] While the page is at the top (scroll position under the 300px threshold), the control is not visible and takes no pointer events."
  BOUND: tests/e2e/back-to-top.spec.ts::back-to-top control stays hidden while the page is at the top
  EXPECT: test-passes
  EVIDENCE: test-passes: 1 bound test(s) exit=0

- [x] T3 returns-to-top
  DEMAND: prove in a real browser that activating the control after scrolling brings window.scrollY back to 0
  SOURCE: "[R-3] Activating the control returns the viewport to the top of the page (`window.scrollY` reaches 0)."
  BOUND: tests/e2e/back-to-top.spec.ts::back-to-top control scrolls the page back to the very top
  EXPECT: test-passes
  EVIDENCE: test-passes: 1 bound test(s) exit=0

- [x] T4 accessible-name
  DEMAND: prove the control is located by ARIA role with accessible name exactly Terug naar boven
  SOURCE: "[R-4] The control is a real button or link whose accessible name is exactly `Terug naar boven`."
  BOUND: tests/e2e/back-to-top.spec.ts::back-to-top control carries the exact Dutch accessible name
  EXPECT: test-passes
  EVIDENCE: test-passes: 1 bound test(s) exit=0

- [x] E1 palette-negative
  CHECK: git add -N src 2>/dev/null; ! git diff d6f01f9e1469 -- src ':(exclude)src/last_modified*' | grep -E '^\+.*(#[0-9a-fA-F]{3,8}|(bg|text|border|ring|from|via|to|fill|stroke|outline|decoration|divide|accent|caret|shadow)-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone|white|black)([-/]|$|[^a-z-]))' && echo palette-clean
  EXPECT: exit=0; `palette-clean`
  SOURCE: "[I-1] Every color in code added for this feature comes from the archive palette tokens: added lines introduce no raw hex colors and no non-archive Tailwind color utilities."
  EVIDENCE: exit=0; 2 clause(s) satisfied; T=/tmp/cr4-gate-2widvx9i

- [x] E2 no-new-deps
  CHECK: git diff --quiet d6f01f9e1469 -- package.json package-lock.json && echo deps-unchanged
  EXPECT: exit=0; `deps-unchanged`
  SOURCE: "no new npm dependencies."
  EVIDENCE: exit=0; 2 clause(s) satisfied; T=/tmp/cr4-gate-zx6oa0n2

- [x] E3 fence-untouched
  CHECK: git diff --quiet d6f01f9e1469 -- src/components/Header.astro src/components/HeaderLink.astro src/components/ThemeToggle.tsx src/components/Search.tsx src/components/Searchbar.astro gen_site && echo fence-clean
  EXPECT: exit=0; `fence-clean`
  SOURCE: "No changes to the header, theme toggle, or search components."
  SOURCE: "No changes under gen_site/ and no changes to GEDCOM data."
  EVIDENCE: exit=0; 2 clause(s) satisfied; T=/tmp/cr4-gate-sgxkkq6g

NO-GATE "the visible/accessible label text is Dutch": covered-by:T4
NO-GATE "No visual-QA machinery; ordinary review judgment only.": review-only

NEVER-RED E1: invariant-over-existing — a negative over the delta; the pre-build delta is empty, so it is vacuously clean before any code exists
NEVER-RED E2: invariant-over-existing — same vacuous-pre-build shape
NEVER-RED E3: invariant-over-existing — same vacuous-pre-build shape
