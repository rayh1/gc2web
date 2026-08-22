CR: specs/back-to-top/back-to-top.cr.md
Spec-sha: 18a2dfa8b8c9
Built-at: 2026-08-22T16:17:03Z

[R-1] MET — built — fixed button in src/components/BackToTop.astro (bottom-6 right-6, z-50), shown once window.scrollY >= 300; included on both layouts via src/components/Footer.astro, which PageLayout.astro and BlogPostLayout.astro both render — test: tests/e2e/back-to-top.spec.ts::back-to-top control appears in the lower-right after scrolling down
[R-2] MET — built — at scroll < 300px the button carries `invisible opacity-0 pointer-events-none` (visibility:hidden + pointer-events:none), toggled by the scroll listener in src/components/BackToTop.astro — test: tests/e2e/back-to-top.spec.ts::back-to-top control stays hidden while the page is at the top
[R-3] MET — built — click handler in src/components/BackToTop.astro calls window.scrollTo({ top: 0, behavior: "smooth" }); test waits for the animation to settle at scrollY 0 — test: tests/e2e/back-to-top.spec.ts::back-to-top control scrolls the page back to the very top
[R-4] MET — built — real `<button type="button">` with aria-label="Terug naar boven" (icon-only SVG is aria-hidden, so the accessible name is exactly the label) in src/components/BackToTop.astro — test: tests/e2e/back-to-top.spec.ts::back-to-top control carries the exact Dutch accessible name

[I-1] MET — built — added code uses only archive palette tokens (border-archive-line, bg-archive-paper, text-archive-accent and their archive-dark counterparts, hover states ditto); the SVG uses stroke="currentColor" and fill="none"; the only non-palette utilities are geometry/behaviour (shadow-lg carries no color family). Gate E1's grep over the delta prints palette-clean. Caveat: `git diff` omits untracked files, so I registered the two new files with `git add -N` (intent-to-add — records paths only, stages no content, commits nothing); after that the gate grep scans all 50 added src lines and still prints palette-clean.

## Test runs (actual results)

- New tests, one file: tests/e2e/back-to-top.spec.ts — 4 passed together (4/4).
- Each test individually via `npx playwright test tests/e2e/back-to-top.spec.ts -g "<title>"`: 1 passed, four times (all four titles above; no title is a substring of another, and no existing suite title contains any of them).
- Full Playwright e2e suite (`npx playwright test` from repo root, after `npm run build`): 30 passed, 0 failed.
- Each requirement's test exercises BOTH layouts inside one test: /entity (PageLayout) and /entity/i00005/ (BlogPostLayout).
- No requirement ids appear inside test code; the mapping lives in this report only.

## Verify pass

`python3 /workspace/.claude/skills/cr4/scripts/verify.py --project . --json` → verdict `incomplete`: the tests lane refused because it detected two test systems (`uv run pytest` and `npm test`) and would not guess which to run. Its own error names the remedy — pass `--tests` explicitly per suite — which I did. A first explicit rerun with `--tests "env -u VIRTUAL_ENV uv run pytest"` failed on collection ImportErrors (wrong working directory: the suite must run from gen_site with `python -m pytest`, exactly how the constitution's own C-1 check invokes it), so the final single pass was:

`python3 /workspace/.claude/skills/cr4/scripts/verify.py --project . --tests "npm test" --tests "bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest'" --json` → stdout saved to .verify/summary.json.

Verdict: **findings** (reported as-is, not rerun to green).
- Lane `constitution`: clean — 1 PASS (C-1), 0 problems.
- Lane `tests`: `npm test` (vitest unit + full Playwright e2e, includes the four new tests) exit 0. The pytest suite exit 1: 53 passed, 4 failed, 1 error. Counts note from the tool: no JUnit report; lane status is from exit codes.

Classification of the five pytest defects — all PRE-EXISTING at baseline d6f01f9e1469, none introduced by this change. Ground for the blanket claim: `git status`/`git diff d6f01f9e1469` show gen_site/, src/content/ and the GEDCOM data byte-identical to baseline; this change adds no Python and touches only Footer.astro, a new Astro component, a new e2e spec file, and specs/back-to-top/. Per failure:
1. ERROR test/test_ascii_tree_generation.py::TestAsciiTreeGeneration::test_generate_individual_page_emits_visible_ascii_tree_block — setUpClass parses the absolute path /workspace/gen_site/Hoofman.ged (outside this repository); gedq answers `source file missing`. Missing external data file in this environment.
2. FAILED test/test_birthday_index.py::TestDateDeterminism::test_no_birth_date_without_a_day_and_month_appears — corpus count 51 != pinned 50; the test pins a count the updated Hoofman.ged (commit 3b0b3a5, Friethoff ingest) has moved.
3. FAILED test/test_birthday_index.py::TestDateDeterminism::test_no_interpreted_birth_date_appears — 53 != pinned 52; same data drift.
4. FAILED test/test_birthday_index.py::TestPlaceholderNames::test_the_six_days_emptied_by_the_rule_are_absent — 06-20 now carries I00333 (Cornelis Friethof, 1794), an entity from the same ingest; the pinned six-empty-days expectation predates it.
5. FAILED test/test_migration_contract.py::TestGedqMigrationContract::test_generated_corpus_matches_baseline_except_allowlist — the generated corpus contains Friethoff-era I003xx/S005xx entity files absent from the git baseline the test compares against; same data drift.

Per the never-move-the-goalposts principle I changed none of these tests or their pins; refreshing them belongs to the corpus-drift effort, not this CR.

## Mechanical gates (run locally, read-only)

- E1 palette-negative: `palette-clean` (after the intent-to-add registration noted under I-1, so the grep genuinely scanned the added lines).
- E2 no-new-deps: `deps-unchanged` — package.json and package-lock.json untouched.
- E3 fence-untouched: `fence-clean` — Header.astro, HeaderLink.astro, ThemeToggle.tsx, Search.tsx, Searchbar.astro, gen_site all untouched.

## Delegated decisions taken

- Placement: a single insertion point — `<BackToTop />` rendered from src/components/Footer.astro, which both layouts include; the control itself is position:fixed so its DOM location does not affect its placement.
- Icon vs text: icon-only (chevron-up SVG, stroke currentColor) with the Dutch label as aria-label; keeps the fixed control small, the accessible name exact.
- Smooth vs instant: smooth (`behavior: "smooth"`), matching the site's existing `scroll-smooth` on `<html>`.
- 300px threshold implementation: a passive `scroll` listener comparing window.scrollY against 300, toggling `visible opacity-100 pointer-events-auto` vs `invisible opacity-0 pointer-events-none` (visibility, not display, so opacity can transition); state also computed once on load.
- Test pages: /entity for PageLayout, /entity/i00005/ for BlogPostLayout — one long page per layout, both exercised inside every test.

## Declined / out of scope

- No fix for the five pre-existing pytest failures (corpus drift + missing external data file) — outside this CR's scope fence and not caused by it.
- No visual-QA machinery, per the scope fence.
- The gates file's T1–T4 BOUND fields are pending; the gates file is read-only for the builder, so binding is left to the reconcile/review stage. The title-to-file mapping it needs is in the [R-n] lines above.
- Nothing committed; specs/birthday-today/birthday-today.cr.md's pre-existing modification left untouched.
