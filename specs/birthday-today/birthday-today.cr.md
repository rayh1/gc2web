---
slug: birthday-today
source: specs/birthday-today/birthday-today-elicited.yaml
code0_ref: 72a52cd6fbac30fb0994230dee6e69689002c7df
---

# Birthday-today block on hoofman.nl

## 1. Intent

Show, on the hoofman.nl homepage, the people from the family tree whose birthday falls on
the day the visitor is looking at the page. <!-- from EL-1 -->

The site is built once into static files, so the list cannot be baked in at build time
without a daily rebuild; it is instead computed in the visitor's browser from an index
generated alongside the site. <!-- from EL-1 --> Roughly two days in three have nobody at
all, so the empty state is the common path rather than an edge case. <!-- from EL-21 -->

## 2. Functional requirements

**[R-1] The homepage shows a birthday block for the visitor's current local date.**
<!-- from EL-1 --> <!-- from EL-2 --> <!-- from EL-19 -->
- AC: With the browser clock set to a date present in the generated index, the homepage
  block lists exactly the individuals recorded under that day; with it set to a date not
  present in the index, the block renders the empty-state line of [R-4]. The date used is
  the visitor's own local date, not a fixed Europe/Amsterdam or UTC date.

**[R-2] Each entry is a linked name followed by one lifespan parenthetical.**
<!-- from EL-15 --> <!-- from EL-16 -->
- AC: Each entry renders the individual's name as a hyperlink to their entity page,
  followed by the lifespan in a single parenthetical using the site's existing
  `lifespan` format, verbatim — `(1890-1972)` with a plain hyphen, and `(1890-?)` when no
  death year is recorded. The birth year does not additionally appear outside the
  parenthetical.
- AC (worked example, verbatim): on 9 March the block shows exactly these three entries,
  in this order:

  ```
  Pieter Hoofman (1833-1874)
  Helena Louisa Walters (1873-1922)
  Anna Maria Christina Hoofman (1893-?)
  ```

  linking to `/entity/i00013/`, `/entity/i00096/` and `/entity/i00012/` respectively.
  <!-- from EL-31 --> <!-- from EL-34 -->

**[R-3] The block is Dutch and uses "born on this day" framing.**
<!-- from EL-17 -->
- AC (verbatim): the block's heading is exactly `Geboren op deze dag`, on every path —
  populated day, empty day, and no-JS alike. The string `verjaardag` appears nowhere in
  the block's rendered output.
  <!-- from EL-31 -->

**[R-4] A day with no eligible birthday still renders the block.**
<!-- from EL-20 --> <!-- from EL-21 -->
- AC: On a date absent from the index the block is present in the DOM. It is not hidden,
  removed, or collapsed.
- AC (verbatim): the line reads exactly `Vandaag is er niemand uit deze stamboom geboren.`
  <!-- from EL-32 -->

**[R-5] A visitor without JavaScript sees a static fallback message.**
<!-- from EL-3 -->
- AC: With JavaScript disabled the block renders a static fallback message and zero
  birthday entries.
- AC (verbatim): the message reads exactly `Deze lijst wordt in je browser samengesteld.
  Zet JavaScript aan om te zien wie er vandaag geboren is.`
  <!-- from EL-33 -->

**[R-6] No withheld individual reaches the generated index, and every eligible one does.**
<!-- from EL-5 --> <!-- from EL-8 --> <!-- from EL-29 -->
- AC: A test over the generated index asserts **both** directions: (a) no individual for
  which `model.Liveness.may_appear_in_aggregate` returns False appears anywhere in the
  index file, and (b) every individual for which it returns True, whose birth date gedq
  treats as deterministic, and whose name is not excluded by [R-10], appears exactly once,
  under their own day. All three qualifiers are load-bearing: without them (b) contradicts
  [R-7] and [R-10].
- AC: That test runs without a browser and without an Astro build — it reads the generated
  index file and the model directly, so it can live in the same suite as
  `test_liveness.py`. `[C-1]`'s promotion from reviewer-assisted to CI-mechanical depends
  on this test being runnable that way.

**[R-7] Only dates gedq treats as deterministic appear.**
<!-- from EL-10 --> <!-- from EL-28 -->
- AC: An individual appears in the index only if gedq's `anniversary` command returns
  their birth as a `BIRT` event. Year-only, month-only and interpreted (`INT`) dates
  therefore never appear.
- AC (property): no individual whose GEDCOM birth date carries an interpreted (`INT`)
  qualifier appears in the index, on any day. 52 individuals carry an `INT` birth date; the
  only two whose `INT` date also carries a day and month — and therefore the only two this
  property can catch on a named day — are `I00129` (`INT 7 JUL 1775 (1840 - 65.12)`) and
  `I00173` (`INT 5 MAR 1755 ()`), quoted verbatim. The other 50 are year-only and are
  already excluded by the year-only AC below.
  <!-- observed: `gedq anniversary Hoofman.ged --date "7 JUL"|"5 MAR" --json` -> 0 BIRT rows whose date contains INT -->
  <!-- observed: awk over BIRT blocks of gen_site/Hoofman.ged -> 52 INT birth dates, 2 carrying a day+month (I00129, I00173); identical at 5042ca9 and de5371a -->
- AC (property): no individual whose birth date is year-only appears in the index — in
  particular 1 January carries only individuals with a literal `1 JAN` birth date, not the
  37 whose year-only dates the Python parser would default onto that day.
  <!-- observed: `gedq anniversary Hoofman.ged --date "1 JAN" --json` -> 1 BIRT row, I00091 '1 JAN 1864' -->
- AC (positive witness): an individual with a plain day-precise date does appear under
  that day — `I00254` (`7 JUL 1881`) under 7 July. Without this, the two properties above
  are satisfiable by an empty index.
  <!-- observed: `gedq anniversary Hoofman.ged --date "7 JUL" --json` -> [('I00254', '7 JUL 1881')] -->

**[R-8] The index carries only days that have content.**
<!-- from EL-30 -->
- AC: The generated index contains a key for a calendar day only when at least one
  eligible individual falls on it. Days with none are absent from the file, and the
  client treats a missing key as an empty day.

**[R-9] Index generation completes without error on every day it queries.**
<!-- from EL-13 --> <!-- from EL-30 -->
- AC: Generating the index raises no error and exits non-zero for no calendar day,
  including 29 February; 29 February yields no entries and, being empty, is absent from
  the index per [R-8].
  <!-- observed: `gedq anniversary Hoofman.ged --date "29 FEB" --json` -> exit 0, {"query_date":"2026-02-29","events":[]}, no stderr -->

**[R-10] Placeholder-named and stillbirth records never appear.**
<!-- from EL-35 -->
- AC: An individual whose given name is a placeholder or a stillbirth marker is excluded
  from the index. The forms present in the corpus, verbatim: `N.N.`, `NN`, `N`,
  `Levenloos`. A birthday entry is never rendered for one of them.
- AC (property): no entry in the index has a name beginning with any of those four tokens.
  <!-- observed: scan of the gedq-realistic pool -> the same 8 matches (I00091, I00097, I00128 'N Walters', I00247/49/50/52 'Levenloos Hofman', I00288 'NN Nillissen') at both anchors; pool size 170 at 5042ca9, 171 at de5371a -->
- AC: 1 January, 7 February, 18 March, 6 June, 20 June and 29 July lose their only entry to
  this rule and therefore render the [R-4] empty state.
  <!-- from EL-36 -->

## 3. Technical constraints and decisions

**Locked**

- The birthday index is emitted by `gen_site` at generation time; withheld individuals
  never enter any shipped file. <!-- from EL-5 -->
- The index is built by calling gedq's `anniversary --json` and filtering its output
  through `model.Liveness.may_appear_in_aggregate`. <!-- from EL-6 -->
- gedq's own `is_alive` flag is **not** the liveness source. Measured at `5042ca9` against
  the then-current `[C-2]` and its 36 withheld individuals: it agrees on only 12, returns
  `None` for 23, and actively disagrees on 1. The withheld set is 38 as of `de5371a`
  (`I00323` and `I00324` joined it, both birth-dateless and presumed living); the agreement
  split has not been re-measured, and the locked decision does not rest on its exact
  figures. <!-- from EL-7 -->
  <!-- observed: `cd gen_site && uv run python scripts/list_living_private.py` -> 38 ids at de5371a, including I00323 and I00324 -->
- "Today" is computed client-side in the visitor's browser; the site remains statically
  built. <!-- from EL-1 -->
- No cron, scheduled rebuild, or other recurring job is introduced. <!-- from EL-4 -->
- Which dates qualify is governed by gedq's determinism filter, not by a second
  reimplementation in `gen_site`. <!-- from EL-28 -->
- Entries sharing a day are ordered **oldest first** (ascending birth year). This
  supersedes `EL-18`'s original delegation — the confirmed worked example in [R-2] fixes
  the order, so it is no longer the builder's choice. <!-- from EL-34 -->
- The Dutch wording of all three block strings is fixed verbatim, not merely framed:
  the heading by [R-3], the empty-state line by [R-4], and the no-JS fallback by [R-5].
  This supersedes `EL-17`'s original delegation — `EL-31`, `EL-32` and `EL-33` are
  user-confirmed worked examples that fix the sentences themselves, so they are no
  longer the builder's choice, exactly as happened to the ordering above.
  <!-- from EL-31 --> <!-- from EL-32 --> <!-- from EL-33 -->

**Delegated — deliberately left to the builder**

- *(none remaining for ordering — see Locked. `EL-18` originally delegated it; the
  confirmed worked example in [R-2] fixed it, so it moved.)*
- *(none remaining for the Dutch wording — see Locked. `EL-17` originally delegated the
  sentences; the confirmed worked examples fixed them, so they moved. A builder must not
  author its own phrasing: three acceptance criteria specify the strings
  character-for-character.)*
- The index file's name, location, and serialization format. The input fixes that it is
  generated and what it must and must not contain, not how it is spelled. <!-- from EL-5 -->

## 4. Invariants and edge cases

- No individual for whom `may_appear_in_aggregate` returns False appears in the birthday
  index, or in any other aggregate output this change adds — filtered out before the file
  is written, not merely hidden at render time. **Scoped to newly added aggregate output,
  matching `[C-1]`.** An unscoped "any shipped artifact" reading would be false of the
  site as it stands: `[C-1]` deliberately exempts the per-person entity pages, the search
  index, the RSS feed and the paginated entity index, all of which predate the rule and
  do publish withheld individuals.
  <!-- from EL-5 --> <!-- from EL-8 -->
  <!-- observed: specs/constitution.md [C-1] exemption clause; withheld I00122, I00323, I00324 each have a committed src/content/entity page and a built dist/entity/ route -->
- 232 of 366 days carry no entry once [R-7] and [R-10] are applied, so [R-4]'s empty state
  is the ordinary path, not an edge case. The index pool is 163 entries across 134 days.
  Counts are as of `de5371a`; at `5042ca9` they were 233 / 162 / 133, and moved when that
  commit refined `I00282`'s birth from `INT 1790 ()` to `22 MAR 1790` — turning 22 March
  from an empty day into a populated one. These counts rot with the data; the commit anchor
  is part of the claim.
  <!-- from EL-21 --> <!-- from EL-36 -->
  <!-- observed: `gedq anniversary Hoofman.ged --date "22 MAR" --json` -> [] at 5042ca9, one BIRT row I00282 '22 MAR 1790' at de5371a; `scripts/list_living_private.py` -> I00282 absent, therefore eligible -->
- No eligible individual currently has a 29 February birthday; with a content-only index
  that day is simply absent. <!-- from EL-13 --> <!-- from EL-30 -->
- Most entries will render as `(YYYY-?)`: 105 of the eligible individuals are PRESUMED
  DECEASED with no recorded death year, as of `de5371a` (107 at `5042ca9`; `I00296` and
  `I00316` gained death dates in that commit and now render a closed lifespan).
  <!-- from EL-16 + lifespan field in src/content/entity/*.md -->
  <!-- observed: DEAT-date diff 5042ca9..de5371a over gen_site/Hoofman.ged -> 4 death dates added (I00296, I00315, I00316, I00318); of those only I00296 (birth 10 APR 1820) and I00316 (birth 5 AUG 1793) carry a day-precise birth and are therefore index entries -->
- **Dependency-drift risk, pinned rather than assumed.** [R-7] adopts gedq's current
  exclusion of `INT` dates, but gedq's own CR-059 AC6 states that "an exact day-month with
  an inexact year appears **without** an ordinal" — and CR-059's verification notes record
  that this clause *could not be exercised*, because gedq's test GEDCOM has no `ABT`/`EST`/
  `CAL` date carrying a day and month. Hoofman.ged has exactly that case. So the behaviour
  [R-7] locks onto is untested upstream and arguably contrary to gedq's own stated AC; if
  gedq is later corrected toward AC6, this index silently gains two people whose day was
  back-computed from an age. [R-7]'s property AC is what turns that silent change into a
  failing test.
  <!-- observed: /workspace/gedq-change-requests/CR-059-anniversary-on-this-day.md lines 153-192 -->
  **Exercised once, and it held (`72a52cd`).** gc2web upgraded the vendored gedq 2.0.1 →
  2.1.0. The behaviour did not move: `7 JUL` still returns only `I00254` and `5 MAR` still
  returns nothing, so `I00129` and `I00173` stayed out of the index. 2.1.0's additions are
  `batch` / `ahnentafel` / `register` / `gaps`, not the anniversary determinism filter. The
  risk is **not** retired — AC6 is still unimplemented upstream and could land in any later
  release — but the pin has now survived one real upgrade.
  <!-- observed: `gedq --version` -> 2.1.0; `gedq anniversary Hoofman.ged --date "7 JUL" --json` -> 1 BIRT row (I00254), `--date "5 MAR"` -> 0 BIRT rows; identical to the 2.0.1 readings above -->
- **Accepted tension:** the index ships publicly and is readable in view-source, so the
  no-JS fallback of [R-5] is presentational only, not a privacy control. The data is
  public either way; `[C-1]` governs what may be in it.
  <!-- from EL-3 --> <!-- from EL-5 -->

## 5. Scope fence — non-goals

- No marriage anniversaries, though gedq returns `MARR` events for the same day.
  <!-- from EL-22 -->
- No death anniversaries, though gedq returns `DEAT` events for the same day.
  <!-- from EL-23 -->
- No upcoming or recent window; strictly today only. This deliberately forgoes the obvious
  workaround for the 62% empty days. <!-- from EL-24 -->
- No notifications, emails, reminders, or RSS items. <!-- from EL-25 -->
- No dedicated route and no site-navigation entry; the homepage block is the whole
  surface. <!-- from EL-19 -->

## Constitution Mapping

Source: `specs/constitution.md`. Each `Check:` clause decomposed on `; ` — neither contains
one, so each yields exactly one sub-clause.

- **[C-1] sub-clause 1** — reviewer-assisted. **Applies at:** the generated birthday index
  and the homepage block; this change adds the first new aggregate output since the rule
  was filed. *Verification hook:* [R-6]'s both-direction test, plus the reviewer running
  `bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python scripts/list_living_private.py'`
  and confirming none of the listed ids is selected.
- **[C-2] sub-clause 1** — CI-mechanical. **Applies at:** `gen_site/model/Liveness.py` and
  the generation path that consumes it; the effort calls the classifier and may extend it
  with day-precision helpers. *Verification hook:* the rule's own command,
  `bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest test/test_liveness.py'`,
  exits 0.

Constitution mapping: 2 non-advisory sub-clauses, 2 applies, 0 not-applicable (2 = 2 + 0)
