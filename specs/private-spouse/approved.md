# Generate the site when a public person's spouse is private

Status: approved

## Goal

gen-site PRD requirement [R-15] (`specs/gen-site/gen-site.prd.md:46`) says an individual whose YAML
note has `private: true` is excluded from all generated output. When such a person is married to a
public person, the family still points to them (PRD edge case [E-2], line 79). Today site
generation then crashes: `GedcomModel` drops private people at load, so `Family.spouse()` returns
None for the private partner, and `individual_link` (`gen_site/gen_site.py:75`) fails on that None
with `AttributeError: 'NoneType' object has no attribute 'name'`. The crash stops the whole build,
so no site update can be published.

After this change the site builds, the private spouse still appears nowhere, and the public people
around them keep their own entries.

## Decisions

- The public spouse's chronology keeps the marriage as a line reading just "Huwelijk" (marriage),
  on the marriage's date, with no partner name or link. Today's line reads "Huwelijk met <link to
  partner>". The marriage is the public person's own life event; only the partner is withheld.
  (user, 2026-11-17)
- The chronology's "Overlijden partner <link>" (partner's death) line is left out when the partner
  is private: showing it would publish the private person's death date. (user, 2026-11-17)
- On the page of a public person who witnessed the marriage, the "Getuige bij" (witness at) entry
  for that marriage names only the public partner. Today it names both partners. (user,
  2026-11-17)
- The same three rules apply when `Family.spouse()` returns None for a family that simply has no
  partner recorded on the other side: that case crashes today for the same reason, and "no partner
  to show" is the same situation.
- The `# type: ignore[...]` comments that hide the None from mypy on those lines, and the comments
  above them saying the crash is left as it is, go: once None is handled they are no longer
  needed. mypy (part of the suite) must still pass.
- The existing test `test_private_spouse_appears_in_no_output` in
  `gen_site/test/test_private_spouse.py` loses its `xfail` marker and must pass; its assertions
  stay as they are. New tests for the criteria below may go beside it. Its fixture
  `gen_site/test/fixtures/private_spouse.ged` gains a death date for I2, so criterion 3's hard case
  is in the data; it is otherwise unchanged.
- Criterion 6 is checked by the reviewer's own comparison for this change, not by a permanent
  test: a test pinned to the base commit would fail on every later change meant to alter the
  pages. `gen_site/test/test_hoofman_pages_unchanged.py` from build 1 is deleted. (user,
  2026-11-17)

## Acceptance criteria

1. Generating the person pages, the source pages and the birthday index from
   `gen_site/test/fixtures/private_spouse.ged` (public I1 Johannes Publiek married on 12 May 1875
   to private I2 Geheimina Verborgen, with public I3 Pieter Getuige as witness) completes without
   an error.
2. In that output there is no page for I2, and no output file contains "I2", "i2/", "Geheimina" or
   "Verborgen". `gen_site/test/test_private_spouse.py`, without its `xfail` marker, shows this and
   passes.
3. I1's page has a chronology line dated 12-05-1875 whose description (the text after the date
   and the optional age, e.g. `- 12-05-1875 (<i>25</i>): Huwelijk`) is exactly "Huwelijk", and no
   "Overlijden partner" line. The hard case is a private partner who has a recorded death date:
   the test must use such a partner so that leaving the death line out is actually exercised.
4. I3's page has a "Getuige bij" entry for that marriage that links I1 and links no one else.
5. A family with one partner and no one on the other side, with a dated marriage and a public
   witness, produces the same "Huwelijk" line on the partner's page, and a "Getuige bij" entry on
   the witness's page that links only that partner, instead of crashing. This case gets its own
   fixture file, e.g. `gen_site/test/fixtures/single_partner.ged`.
6. The person and source pages generated from `gen_site/Hoofman.ged` by the new code are
   byte-identical to those the base code generates, both written to temporary folders (not to
   `src/`). `Hoofman.ged` has no family with a missing or private-only-on-one-side partner, so no
   page may change. Every existing test still passes.

## Context

- Base: `4e2dcc27bc5b814143c06164e977c478bc145186` (HEAD of `main` when the change began; the
  working tree was clean).
- Test suite, from a clean state: on the host, from `/workspace/gc2web`, run
  `bash .devcontainer/ci.sh` (builds the dev-container image from the working tree, runs
  `.devcontainer/check.sh` in a fresh container: dependency install, ruff check and format, pytest,
  the npm checks, osv-scanner, mypy; exit 0 is a pass; about 3 minutes). Then the constitution
  runner, also on the host from `/workspace/gc2web`:
  `python3 /workspace/.claude/skills/create-constitution/scripts/constitution-ci.py --project .`
  (rule [C-1], the privacy rule; exit 0 is a pass).
- Warning: the constitution runner above, and any host `pytest` run that includes
  `gen_site/test/test_migration_contract.py` (a bare host `uv run pytest` does), writes into the
  real site: that test's `setUpClass` runs `python gen_site.py Hoofman.ged`, i.e. `main()`. After
  such a run, check `git status -- src/` and restore with `git checkout -- src/` (found in
  `01-build.md`). `ci.sh` is unaffected: it runs in a throwaway container.
- Quick run of the one test, in the container or on the host:
  `uv run pytest gen_site/test/test_private_spouse.py`.
- The crash sites at the base: `gen_site/gen_site.py:238-247` (in `generate_chronology`: the
  marriage line and the partner's-death line), `gen_site/model/Individual.py:353-355` (in
  `witnessed_events`, which the "Getuige bij" section at `gen_site.py:500-508` renders).
  `Family.spouse()` is at `gen_site/model/Family.py:107`.
- Places that already handle a None spouse and need no change: `relationship_summary_str`
  (`gen_site.py:146`), the family section (`gen_site.py:428`; children are listed outside the
  spouse guard), residences with a spouse (`Individual.locations`, rendered with
  `if location.spouse`), and the ASCII family tree (`gen_site/util/AsciiTreeRenderer.py:163`).
- Never run `gen_site.py main()` on the fixture: it writes into the real site
  (`src/content/entity/`, `src/data/birthday-index.json`, `src/last_modified.ts`;
  `gen_site.py:24-32`).
- The fixture has one source (S1) only because gedq prints `[]` for an empty
  `search --expand --json`, which crashes gc2web's gedq reader; that is parked separately and is
  not part of this change.
- Known limit, not handled: free text (a source's title or text, a note) that spells out a private
  person's name is published as written. No such case has been seen.
- Separate from this change: a private person who is a witness at someone else's event is shown by
  name, as plain text without a link (`witness_str`, `gen_site.py:181-198`); PRD edge case [E-5]
  (line 82) specifies that. No private person in `Hoofman.ged` is a witness. The user chose to
  keep this out of the change (2026-11-17).
- `gen_site/test/test_ascii_tree_generation.py:13` hardcodes the container path
  `/workspace/gen_site/Hoofman.ged`, so on the host that test errors; the full suite runs in the
  container through `ci.sh`.
- The committed pages in `src/content/entity/` predate gc2web commit 9694a35 (place parts joined
  with ", "), so a fresh generation differs from them on three pages; that is why criterion 6
  compares base-code output with new-code output rather than with `src/`.
- Spec review: 2026-11-17T22:24:01+01:00 – 2026-11-17T22:31:38+01:00
