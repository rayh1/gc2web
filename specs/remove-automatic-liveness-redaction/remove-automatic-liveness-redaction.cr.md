---
slug: remove-automatic-liveness-redaction
source: specs/birthday-today/birthday-today.cr.md + inline-cr
---

# Birthday-today homepage block without automatic liveness redaction

## Intent

Show, on the hoofman.nl homepage, the people from the family tree whose birthday falls on
the day the visitor is looking at the page. <!-- from CR:birthday-today:intent -->

The site is built once into static files, so the list is computed in the visitor's browser
from an index generated alongside the site; that index publishes every individual selected
for that day except those carrying the manual `private: true` note. No automatic liveness
inference is applied. <!-- from CR:birthday-today:intent --> <!-- from CR:remove-automatic-liveness-redaction:intent -->

## Functional requirements

- **[R-1] Delete the automatic liveness classifier and every use of it.**
  Remove `gen_site/model/Liveness.py` in full; remove the `may_appear_in_aggregate` filter in
  `build_birthday_index` so no individual is excluded by inferred liveness; delete
  `gen_site/scripts/list_living_private.py` (a classifier-reporting script with no other caller).
  **AC:** `grep -rnE 'may_appear_in_aggregate|Liveness|LivenessStatus|LIVING_PRIVATE|LIVING_MAX_AGE|EVENT_RECENCY' gen_site --include=*.py` returns exit 1 with no matches.
  <!-- from CR:remove-automatic-liveness-redaction:R-1 -->

- **[R-2] Retain the manual privacy exclusion as the sole redaction.**
  An individual carrying `private: true` in a note stays excluded from all output via
  `GedcomModel.__exclude_privates`; no other individual is withheld.
  **AC:** for a fixture where individual `A` has `private: true` and individual `B` has a birthday
  on the same reference day without a private note, `A` is absent from the birthday block and `B`
  is present.
  <!-- from CR:remove-automatic-liveness-redaction:R-2 -->

- **[R-3] Replace constitution rules [C-1], [C-2], [C-3] with one positive privacy rule.**
  `specs/constitution.md` keeps exactly one Privacy & Publication Policy rule, verbatim:
  `The only publication redaction is the manual private: true note: an individual carrying private: true in a note is excluded from all output — per-person entity pages and every aggregate output alike. No automatic liveness inference is applied; the source GEDCOM is internet-sourced data already subject to upstream privacy restrictions.`
  **AC:** the rule's Check is exactly `bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest test/test_migration_contract.py -k test_private_people_are_excluded'`; the old Privacy & Publication Policy wording no longer mentions `may_appear_in_aggregate`, `110`, `95`, `LIVING/PRIVATE`, `test_liveness.py`, or `test/test_aggregate_privacy.py`.
  <!-- from CR:remove-automatic-liveness-redaction:R-3 -->

- **[R-4] Remove the dead liveness tests and repair the surviving privacy guard.**
  Delete `gen_site/test/test_liveness.py` and `gen_site/test/test_aggregate_privacy.py`; remove
  liveness assertions from `gen_site/test/test_birthday_index.py`; repair
  `gen_site/test/test_migration_contract.py::test_private_people_are_excluded` so it points at the
  real repo tree and asserts both sides of the privacy rule.
  **AC:** `pytest test/test_birthday_index.py` passes with zero liveness references; `pytest test/test_migration_contract.py -k test_private_people_are_excluded` executes at least one assertion for private excluded and one for non-private retained, then exits 0.
  <!-- from CR:remove-automatic-liveness-redaction:R-4 -->

- **[R-5] The homepage shows a birthday block for the visitor's current local date.**
  The homepage renders a birthday block whose populated or empty content is chosen from the
  visitor's own browser-local date, not from a fixed Europe/Amsterdam or UTC date.
  **AC:** with the browser clock set to a day present in the generated index, the homepage block
  lists exactly the individuals recorded under that day; with it set to a day absent from the
  index, the block renders the empty-state line of [R-7].
  <!-- from CR:birthday-today:R-1 -->

- **[R-6] Each populated entry is a linked name followed by one lifespan parenthetical, oldest first.**
  **AC:** each entry renders the individual's name as a hyperlink to their entity page, followed by
  the lifespan in a single parenthetical using the site's existing `lifespan` format verbatim:
  `(1890-1972)` with a plain hyphen, and `(1890-?)` when no death year is recorded.
  **AC (worked example, verbatim):** on 9 March the block shows exactly these three entries, in
  this order: `Pieter Hoofman (1833-1874)`, `Helena Louisa Walters (1873-1922)`, and
  `Anna Maria Christina Hoofman (1893-?)`, linking to `/entity/i00013/`, `/entity/i00096/`, and
  `/entity/i00012/` respectively.
  <!-- from CR:birthday-today:R-2 -->

- **[R-7] The block uses fixed Dutch strings for the heading, empty state, and no-JavaScript fallback.**
  **AC:** the heading is exactly `Geboren op deze dag` on populated, empty, and no-JS paths; the
  string `verjaardag` appears nowhere in the block's rendered output.
  **AC:** on a date absent from the index, the block remains present in the DOM and the line reads
  exactly `Vandaag is er niemand uit deze stamboom geboren.`
  **AC:** with JavaScript disabled, the block renders zero birthday entries and the message reads
  exactly `Deze lijst wordt in je browser samengesteld. Zet JavaScript aan om te zien wie er vandaag geboren is.`
  <!-- from CR:birthday-today:R-3 --> <!-- from CR:birthday-today:R-4 --> <!-- from CR:birthday-today:R-5 -->

- **[R-8] The generated birthday index is derived from gedq's deterministic `BIRT` results only.**
  An individual appears in the index only if `gedq anniversary --json` returns their birth as a
  `BIRT` event for that calendar day.
  **AC:** year-only, month-only, and interpreted (`INT`) birth dates never appear in the index.
  **AC (positive witness):** `I00254` (`7 JUL 1881`) appears under 7 July.
  <!-- from CR:birthday-today:R-7 -->

- **[R-9] The generated index contains only content-bearing days and generation succeeds for all calendar days.**
  **AC:** the generated index contains a key for a calendar day only when at least one eligible
  individual falls on it; missing keys are treated by the client as empty days.
  **AC:** generating the index exits successfully for every queried day, including 29 February; if
  29 February has no eligible individual, it is absent from the file rather than emitted as an
  empty key.
  <!-- from CR:birthday-today:R-8 --> <!-- from CR:birthday-today:R-9 -->

- **[R-10] Placeholder-named and stillbirth records never appear in the birthday output.**
  An individual whose given name is a placeholder or stillbirth marker is excluded from the index.
  The forms present in the corpus are `N.N.`, `NN`, `N`, and `Levenloos`.
  **AC:** no generated birthday entry begins with any of those four tokens.
  **AC:** 1 January, 7 February, 18 March, 6 June, 20 June, and 29 July render the [R-7]
  empty-state line because their only candidate is excluded by this rule.
  <!-- from CR:birthday-today:R-10 -->

## Technical constraints & decisions

- **Locked** — the birthday block is emitted from the homepage and reads from an index generated by
  `gen_site` at build time; no cron, scheduled rebuild, or recurring job is introduced.
  <!-- from CR:birthday-today:Locked -->
- **Locked** — `today` is computed client-side in the visitor's browser; the site remains
  statically built.
  <!-- from CR:birthday-today:Locked -->
- **Locked** — the birthday block and all aggregate output show every non-private individual; no
  age or year cutoff survives anywhere in the code.
  <!-- from CR:remove-automatic-liveness-redaction:Locked -->
- **Locked** — `private: true` honouring is the only retained redaction.
  <!-- from CR:remove-automatic-liveness-redaction:Locked -->
- **Locked** — which births qualify is governed by gedq's determinism filter, not by a second
  reimplementation in `gen_site`.
  <!-- from CR:birthday-today:Locked -->
- **Locked** — entries sharing a day are ordered oldest first (ascending birth year).
  <!-- from CR:birthday-today:Locked -->
- **Locked** — the Dutch wording of the heading, empty-state line, and no-JS fallback is fixed
  verbatim by [R-7].
  <!-- from CR:birthday-today:Locked -->
- **Locked** — the constitution keeps a positive privacy rule rather than silence.
  <!-- from CR:remove-automatic-liveness-redaction:Locked -->
- **Delegated** — the birthday index file's exact name, location, and serialization format are left
  to the builder.
  <!-- from CR:birthday-today:Delegated -->
- **Delegated** — the exact placement and house-style wording of the replacement `[C-1]` within
  `specs/constitution.md` is left to the constitution author; this CR fixes the rule's meaning and
  Check, not its final prose formatting.
  <!-- from CR:remove-automatic-liveness-redaction:Delegated -->

## Invariants & edge-cases

- A `private: true` individual never appears in any output — before or after this change.
  <!-- observed: gen_site/model/GedcomModel.py:25 -->
- Placeholder and stillbirth filtering (`N.N.`, `NN`, `N`, `Levenloos`) is not liveness and stays
  in force after the classifier is removed.
  <!-- from CR:birthday-today:R-10 --> <!-- from CR:remove-automatic-liveness-redaction:Invariant -->
- Individuals with no recorded death event who are not manually private are deliberately published
  by the birthday block after this change.
  <!-- from CR:remove-automatic-liveness-redaction:Invariant -->
- A day absent from the generated index is a valid and common path; the homepage still renders the
  block and shows the [R-7] empty-state line.
  <!-- from CR:birthday-today:R-4 -->
- The no-JavaScript fallback is presentational only; the generated birthday index is public data,
  so privacy is enforced before the file is written, not by hiding it in the browser.
  <!-- from CR:birthday-today:Invariant --> <!-- from CR:remove-automatic-liveness-redaction:R-2 -->

## Scope fence (non-goals)

- Does **not** change GEDCOM date parsing — deterministic date selection still comes from `gedq anniversary`.
  <!-- from CR:birthday-today:Scope --> <!-- from CR:remove-automatic-liveness-redaction:Scope -->
- Does **not** change the `(birth-death)` lifespan format.
  <!-- from CR:remove-automatic-liveness-redaction:Scope -->
- Does **not** add marriage anniversaries or death anniversaries.
  <!-- from CR:birthday-today:Scope -->
- Does **not** add notifications, emails, RSS items, or a dedicated birthday route.
  <!-- from CR:birthday-today:Scope -->
- Does **not** change per-person entity pages beyond removing automatic liveness redaction; they
  already publish all non-private individuals.
  <!-- from CR:remove-automatic-liveness-redaction:Scope -->

## Constitution Mapping

`specs/constitution.md` found and governing. `create-constitution/scripts/constitution-ci.py --list`
reports `[C-1] RUNNABLE`, so it is runner-enforced and not mapped.
<!-- observed: `python3 /workspace/.claude/skills/create-constitution/scripts/constitution-ci.py --project /workspace/gc2web --list` -> [C-1] RUNNABLE -->

Constitution mapping: 1 non-advisory sub-clause = 0 mapped (runner won't run — REVIEWER/UNSUPPORTED; 0 applies, 0 not-applicable, 0 = 0 + 0) + 1 runner-enforced (RUNNABLE/PARTIAL, not mapped).

## Self-checks

- **[I-1] Traceability** — every element is grounded in the existing `birthday-today` CR, the
  original redaction-removal CR, or an observed command/file reference recorded above. No findings.
- **[I-2] Coherence** — `[R-1]` and `[R-2]` replace the old liveness-qualified publication rule
  with manual-only privacy without conflicting with the birthday-block feature requirements in
  `[R-5]` through `[R-10]`. No findings.
