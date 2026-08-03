# gc2web Constitution

## Purpose & Scope

App-wide constraints for gc2web — the static genealogy site generated from a GEDCOM into Astro
content. Every rule here holds for every feature: new work is checked against them by
`create-review`'s gate `Gc`, and the CI-mechanical ones by the constitution CI runner.
Per-feature requirements belong in a PRD, implementation detail in a Design Document, and
agent-behaviour guidance in `CLAUDE.md` — none of those belong here.

## Privacy & Publication Policy

- [C-1] The only publication redaction is the manual `private: true` note: an individual
  carrying `private: true` in a note is excluded from all output — per-person entity pages and
  every aggregate output alike. No automatic liveness inference is applied; the source GEDCOM
  is internet-sourced data already subject to upstream privacy restrictions.
  Check: (CI-mechanical) `bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest test/test_migration_contract.py -k test_private_people_are_excluded'` exits 0.

## Revision Notes

- 2026-07-26 — File created (create mode, single-rule on-ramp delegated by `capture-rule`).
  1 rule: 0 CI-mechanical, 1 reviewer-assisted, 0 advisory. `[C-1]` filed reviewer-assisted
  rather than CI-mechanical because "which generated pages count as aggregate output" has no
  mechanical handle in this repo yet (no marker, no directory convention, no frontmatter `kind`),
  and a CI form would have to pin the rule to a surface invented now — any future aggregate page
  not adopting it would escape (no-narrowing rule). Promotion trigger: once an aggregate output
  exists, `tend-constitution` can promote `[C-1]` to CI-mechanical by asserting over the built
  site that no non-entity route in `dist/` references an entity ID from the ineligible set.
  Grounding (repo audit, 2026-07-25): `gen_site` carries no living-person filtering; 316
  generated person pages, of which 150 carry no recorded death year (106 render `(YYYY-?)`,
  44 render `(?-?)`); source GEDCOM has 163 of 322 individuals without a death event, 12 of
  them born 1935 or later. Scope decided by the user: additive, new output only; existing
  per-person pages intentionally published. No `Why:` line carried — the drafted rationale was
  skill-authored, not user-authored, and the no-synthesis mandate forbids carrying it.

- 2026-07-26 — Revised `[C-1]` and added `[C-2]` (scope: Privacy & Publication Policy).
  Testability screen: 2 rules, 1 CI-mechanical, 1 reviewer-assisted, 0 advisory. Pedagogical
  density delta: +1 rule, no `Why:` or `Example:` carried on either (skipped with reason: no
  user-authored rationale supplied); no category preambles added.

  `[C-1]` now defers the "who" to `[C-2]` instead of using "no recorded death event", which was
  a crude proxy that withheld 149 people — including 18th–19th-century individuals whose deaths
  were simply never recorded. It stays reviewer-assisted: the classifier is Python in `gen_site`
  while the aggregate consumers are Astro/TypeScript, so no faithful mechanical check exists
  until liveness data crosses that language boundary. Promotion trigger: once the birthday
  feature settles how liveness reaches the page layer (a frontmatter label, a Python-generated
  aggregate, or a page-layer port), `tend-constitution` promotes `[C-1]` to CI-mechanical with a
  full calibration gate. Assist command verified from the project root, exit 0.

  `[C-2]` is implemented at `gen_site/model/Liveness.py` (`LIVING_MAX_AGE_YEARS = 110`,
  `EVENT_RECENCY_YEARS = 95`, both mirrored in the rule text) and pinned by
  `gen_site/test/test_liveness.py` (19 tests). Calibration gate, all four arms run: plant A
  (constant `110` -> `100`) FAILED 2/17, exit 1; plant B (comparison `<=` -> `<`) FAILED 1/18,
  exit 1; baseline 19 passed, exit 0; compliant probe (a new consumer calling
  `may_appear_in_aggregate`) 19 passed, exit 0; tree verified byte-identical by sha256 after
  each revert. Named deviation: the two plants differ in construct form but NOT in file, because
  this rule governs exactly one module — there is no second file for a threshold to live in.
  Overfit caught and fixed during calibration: the first version of the test derived its
  boundary years FROM the constants, so `110` -> `100` passed 18/18; boundary years are now
  literal (1916/1915, 1931/1930) plus an explicit constant assertion.

  `[C-2]`'s `Check:` command is wrapped in `bash -c '…'` deliberately — do NOT "simplify" it to
  a `(cd gen_site && …)` subshell. The constitution CI runner prefixes any command whose argv0
  is not a plain system tool with `uv run`, so a parenthesised subshell becomes
  `uv run (cd gen_site && …)`, which hands `uv` the literal token `(cd` and exits 2 — a FALSE
  violation. `bash` is on the runner's system-tool list, so this form runs unwrapped. Verified:
  the runner reports `[C-2] PASS … exit 0`.

  CORRECTION to the genesis entry above (append-only, so corrected here rather than edited):
  it states "`gen_site` carries no living-person filtering". That is FALSE. gc2web has a manual
  per-individual privacy flag — `private: true` in a note -> `NotesMixin.is_private` ->
  `GedcomModel.__exclude_privates` removes them from the model at parse time — covering 6
  individuals. What `gen_site` lacked was *automatic liveness inference*, which `[C-2]` adds.
  The false claim came from grepping "privacy" when the symbol is "privates".
  Caveat on that mechanism's guard: `test_private_people_are_excluded` exists but does NOT
  currently run — `test_migration_contract.py` hardcodes `WORKSPACE_DIR = Path("/workspace")`
  while the repo lives at `/workspace/gc2web`, so all 9 of its tests error with
  `FileNotFoundError: /workspace/gen_site`. The manual privacy flag is therefore unguarded in
  practice until that path is fixed. Pre-existing, unrelated to this change.

  CORRECTION to the genesis numbers: "150 with no recorded death year" was a crude proxy.
  Authoritative figures from the real parser over the 316 published individuals: 173 DECEASED,
  88 PRESUMED DECEASED, 55 LIVING/PRIVATE, 261 eligible for aggregate output. Interim figures of
  62 and 56 were regex artifacts — a throwaway script read `INT 1919 (21 in 1940)`, a GEDCOM
  interpreted date, as 1940 rather than 1919.

  Validation signal: `[C-2]` classifies all 6 manually-flagged private individuals as
  LIVING/PRIVATE, reproducing every human curation call. `[C-2]` composes with, never replaces,
  the manual flag: `may_appear_in_aggregate` returns False when `is_private()` is true OR
  liveness is LIVING/PRIVATE. Accepted gap: a GEDCOM tag with no sub-lines at all (a bare
  `1 DEAT`) is indistinguishable from an absent tag in this model and reads as no evidence;
  Hoofman.ged contains zero such tags.

- 2026-07-27 — Revised `[C-2]`: the marriage-recency and child-recency tests now apply **only
  when no birth year can be parsed**. They are proxies for an unknown birth date; under the
  previous literal reading ("any of these applies") a known birth year beyond 110 was overridden
  by a late marriage or child, withholding 19 individuals in Hoofman.ged born 1892–1912 — aged
  114–134, certainly dead. Surfaced by an `/elicit` run on the birthday-list feature
  (`specs/birthday-today/birthday-today-elicited.yaml`, fact `EL-11`) and confirmed by
  measurement before the change. Rule statement, `gen_site/model/Liveness.py`, and
  `gen_site/test/test_liveness.py` updated together; the `Check:` clause is unchanged.
  Measured effect: withheld 55 -> **36**; day-precise birthday pool 158 -> **172**; calendar days
  with no eligible birthday 235 -> **226** of 366. Full split now 173 DECEASED / 107 PRESUMED
  DECEASED / 36 LIVING/PRIVATE over the 316 published individuals.
  Re-calibration on touch (mandatory — the test was edited), all four arms run: plant A
  (constant `110` -> `100`) FAILED 3/19, exit 1; plant B (control flow — the known-birth early
  return deleted, reverting to the old any-condition reading) FAILED 2/20, exit 1; baseline 22
  passed, exit 0; compliant probe 22 passed, exit 0; tree verified byte-identical by sha256 after
  each revert. Plant B deliberately targets the new scoping rather than a threshold, so the
  change itself — not just the numbers — is guarded. Testability screen unchanged: 2 rules,
  1 CI-mechanical, 1 reviewer-assisted, 0 advisory. No `Why:`/`Example:` added.

- 2026-07-28 — Promoted `[C-1]` to CI-mechanical, split `[C-3]` out of it, and repaired `[C-2]`'s
  test. Surfaced by a `tend-constitution` sweep. Testability screen: 3 rules, **2 CI-mechanical,
  1 reviewer-assisted, 0 advisory**. Pedagogical density: 3 rules, 0 carry `Why:` (1 new rule
  skipped with reason: no user-authored rationale supplied), 0 carry `Example:` (same reason),
  0 category preambles — unchanged practice from the entries above.

  `[C-1]`'s promotion trigger, filed 2026-07-26 as "once the birthday feature settles how liveness
  reaches the page layer", is met: liveness now reaches it as a Python-generated aggregate
  (`src/data/birthday-index.json`, written by `gen_site/birthday_index.py`). The new check is the
  **general** form the genesis entry proposed — assert over the built site that no non-entity route
  in `dist/` references an id from the ineligible set — implemented at
  `gen_site/test/test_aggregate_privacy.py`. A per-feature assertion was rejected: it would guard
  only the surface it was written for, so the next aggregate page escapes silently, which is the
  no-narrowing objection that kept `[C-1]` reviewer-assisted in the first place. The test therefore
  scans everything and carries an explicit exemption list of exactly the four surfaces `[C-1]` names
  as predating the rule, plus the sitemaps, which mirror those routes rather than selecting anyone.
  Adding an exemption is a visible edit to that list.
  Calibration gate, all four arms run: plant A (a NEW unfiltered aggregate route,
  `src/pages/living.astro`) FAILED 1/3, exit 1; plant B (the liveness filter deleted from
  `gen_site/birthday_index.py`, index regenerated) FAILED 1/3, exit 1; baseline 3 passed, exit 0;
  compliant probe (a new aggregate route consuming the filtered index) 3 passed, exit 0. The two
  plants differ in **both file and construct form**, so the same-file deviation named for `[C-2]`
  does not apply here. Tree verified byte-identical by sha256 after each revert.
  `[C-1]`'s `Check:` is wrapped in `bash -c '…'` for the same reason `[C-2]`'s is, and the reason is
  now sharper: the CI runner's system-tool list is
  `{git, grep, ls, find, diff, cmp, cat, test, sh, bash}`, so `npm` and a `(cd …)` subshell both get
  prefixed with `uv run` and fail spuriously. The previous `[C-1]` Check used exactly that
  parenthesised form — harmless while the runner skipped reviewer-assisted rules, a false violation
  the moment it did not.

  **`[C-3]` is a split, not a new obligation.** The retired `[C-1]` Check carried two clauses: that
  no withheld individual is selected, and that the selection *routes through*
  `may_appear_in_aggregate`. The `dist/` scan decides the first mechanically and generally but
  cannot see the second — a page hand-rolling its own correct filter passes the scan while bypassing
  the single selection path. Rather than let the promotion silently drop that clause to inflate the
  CI-mechanical count, it is preserved in scope as `[C-3]`, reviewer-assisted, with a grep assist
  over both the Astro and the Python selection sites.

  **`[C-2]`'s rule text is unchanged; its test was repaired.** The mandatory calibration re-audit
  found `[C-2]` **uncalibrated**: a realistic plant restricting `_child_birth_years` to the first
  child of the first family passed all 22 tests, exit 0. That is not a hygiene defect — the rule
  says "a child was born 95 years ago or less", meaning *any* child, so under the plant someone
  whose first child was born 1890 and second in 1935 is classified PRESUMED DECEASED and published.
  The 2026-07-27 audit missed it because both its plants targeted `classify`'s threshold and control
  flow; neither touched the helper traversal, and the suite exercised `_marriage_years` across two
  families but `_child_birth_years` only with one family holding one child. Two tests were added
  (`test_the_most_recent_child_decides_across_families`,
  `test_the_most_recent_child_decides_within_one_family`), both placing the OLD child first so a
  truncating traversal is caught. Re-calibration on touch, all four arms: plant A (constant
  `EVENT_RECENCY_YEARS` `95` -> `85`) FAILED 6/24, exit 1; plant B (the previously-escaping
  traversal truncation) FAILED 2/24, exit 1; baseline 24 passed, exit 0; compliant probe 24 passed,
  exit 0; tree byte-identical by sha256 after each revert. Named deviation, carried forward
  unchanged: `[C-2]`'s two plants differ in construct form but NOT in file, because this rule
  governs exactly one module.

- 2026-08-03 — Replaced Privacy & Publication Policy `[C-1]`/`[C-2]`/`[C-3]` with one positive
  rule: the only publication redaction is the manual `private: true` note, and no automatic
  liveness inference is applied. The liveness classifier module, its aggregate-selection caller,
  and its dedicated tests were removed in the same build; the surviving privacy guard is now
  `gen_site/test/test_migration_contract.py -k test_private_people_are_excluded`. Testability
  screen: 1 rule, 1 CI-mechanical, 0 reviewer-assisted, 0 advisory. Pedagogical density: 1 rule,
  0 carry `Why:`, 0 carry `Example:`, 0 category preambles.
