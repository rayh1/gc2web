Started: 2026-11-17T22:55:44+01:00
Finished: 2026-11-17T23:00:45+01:00

# Review 3: private spouse (base 4e2dcc2, tip ddf2ef0)

I did not write the spec, build or fix any part of this change.

## Acceptance criteria

1. **Met.** Spec: "Generating the person pages, the source pages and the birthday index from
   `gen_site/test/fixtures/private_spouse.ged` … completes without an error." Evidence:
   `test_private_spouse_appears_in_no_output` calls `generate_individual_pages`,
   `generate_source_pages` and `generate_birthday_index` on that fixture and passed in my suite
   run. On the base code, the test failed in my base run with
   `gen_site/gen_site.py:75: AttributeError: 'NoneType' object has no attribute 'name'`. My own
   run of all three generators at the tip wrote `I1.md`, `I3.md`, `S1.md` and
   `birthday-index.json` with no error. At the base, the same run raised the AttributeError.
2. **Met.** Spec: "there is no page for I2, and no output file contains "I2", "i2/",
   "Geheimina" or "Verborgen". `gen_site/test/test_private_spouse.py`, without its `xfail`
   marker, shows this and passes." Evidence: the diff only removes the `@pytest.mark.xfail(...)`
   decorator, and the test body (`assert not (tmp_path / "I2.md").exists()` plus the leak loop)
   is unchanged context. The test passed at the tip and failed at the base with the
   AttributeError. A grep for those four strings over my own tip output found nothing. The
   birthday index at the tip lists only I3 (`01-01`) and I1 (`03-03`).
3. **Met.** Spec: "I1's page has a chronology line dated 12-05-1875 whose description … is
   exactly "Huwelijk", and no "Overlijden partner" line. … the test must use such a partner"
   (a private partner with a recorded death date). Evidence: the fixture diff adds
   `1 DEAT / 2 DATE 4 FEB 1890` under I2. `test_public_spouse_keeps_marriage_without_private_partner`
   asserts `[e for e in entries if e[0] == "12-05-1875"] == [("12-05-1875", "Huwelijk")]`, that
   no description starts with "Overlijden partner", and that no line is dated 04-02-1890. My tip
   output shows `- 12-05-1875 (<i>25</i>): Huwelijk` and no partner's-death line. The test
   failed at the base. It also failed against two mutants I made of the tip: the marriage line
   changed to `"Huwelijk met ?"`, and an `"Overlijden partner"` line added when the spouse is None.
4. **Met.** Spec: "I3's page has a "Getuige bij" entry for that marriage that links I1 and links
   no one else." Evidence: `test_witness_entry_names_only_public_partner` asserts exactly one
   `- Huwelijk ` entry dated `op 12 MAY 1875`, Markdown links exactly
   `[("Johannes Publiek", "../i1/")]`, and every `href` a source page. My tip output is
   `- Huwelijk [Johannes Publiek](../i1/) op 12 MAY 1875 te Graauw`. The test failed at the base.
   It also failed against two witness mutants: the people list `[individual, individual]`, and
   an empty list when the spouse is None.
5. **Met.** Spec: "A family with one partner and no one on the other side, with a dated
   marriage and a public witness, produces the same "Huwelijk" line … and a "Getuige bij" entry
   … that links only that partner … This case gets its own fixture file". Evidence:
   `gen_site/test/fixtures/single_partner.ged` has `F1` with only `1 HUSB @I1@`, `MARR` dated
   20 JUN 1876, and witness `xref_id: I3`. `test_family_without_other_partner` asserts
   `("20-06-1876", "Huwelijk")`, no "Overlijden partner", and one witness entry linking only
   `[Cornelis Alleen](../i1/)`. My tip output matches that. The test failed at the base with the
   AttributeError, and it failed against all four mutants above.
6. **Met.** Spec: "The person and source pages generated from `gen_site/Hoofman.ged` by the new
   code are byte-identical to those the base code generates, both written to temporary folders
   (not to `src/`). … Every existing test still passes." Evidence: I generated the pages with
   `GedcomModel().parse_file('Hoofman.ged')` plus `generate_individual_pages` and
   `generate_source_pages` into separate scratch folders, once from a base worktree and once from
   a tip worktree. Each run wrote 907 files (345 person pages, 562 source pages).
   `diff -r` reported no difference, and the sha256 over all files was
   `4b2bc452…5dbb3cc9c` for both. `/workspace/gc2web/src/` stayed clean (`git status -- src/`
   empty). For the second sentence, the whole suite passed (see `Suite:`). The diff changes or
   removes no existing test apart from the `xfail` marker that the spec's Decisions remove
   ("loses its `xfail` marker and must pass; its assertions stay as they are"). The fixture gains
   I2's death date, which the Decisions also call for ("gains a death date for I2").
   `test_hoofman_pages_unchanged.py` is absent at the tip, as the Decisions require.

Decisions also checked: the `# type: ignore[...]` comments and the "left as it is" comments are
gone (a grep for "left as it is" and "privacy-excluded" in `gen_site/*.py` at the tip found
nothing), and mypy passed ("Success: no issues found in 24 source files").

Neighbours: the only callers are `generate_individual_page` (`gen_site.py:466`, the chronology)
and `gen_site.py:504` plus `Individual.all_sources` (`Individual.py:326`, the witnessed events).
`all_sources` reads only the event, so a shorter people list does not affect it. The fixtures
are loaded only by `test_private_spouse.py`. No test or script finds `.ged` fixtures by pattern.

## Timed runs

Install: `bash .devcontainer/ci.sh` image build plus the fresh-container `uv sync` and `npm ci`
inside `check.sh`, from a full local clone checked out at `ddf2ef0` (`Installed 37 packages`,
`added 552 packages … in 6s`) — passed — included in the Suite wall-clock time below (not timed
separately)
Suite: `time bash .devcontainer/ci.sh` (full clone at `ddf2ef0`) — exit 0: ruff check and format
passed, pytest `62 passed`, vitest 6 passed, Playwright 30 passed, both osv-scanner scans
"No issues found", mypy passed — 1m36.8s. A first run from a `git worktree` exited 1. The two
`test_migration_contract.py` tests that call `git` failed there because a worktree's `.git` is a
pointer file that does not work inside the image. That was my setup, not the build, so I re-ran
from a full clone.
Constitution run: `time python3 /workspace/.claude/skills/create-constitution/scripts/constitution-ci.py --project .`
(tip worktree) — exit 0, `[C-1] PASS` — 11.7s
Base run: `time (uv sync && uv run pytest gen_site/test/test_private_spouse.py)` in a base
worktree with the tip's test file and both fixtures copied in (no dependency files changed) —
`4 failed`, each with `AttributeError: 'NoneType' object has no attribute 'name'` from
`individual_link` — 7.2s

Constitution: none (`--list` reports the only rule, [C-1], as RUNNABLE, so the runner decides
it: PASS. There are no REVIEWER, UNSUPPORTED or PARTIAL rules, and the diff does not touch
`specs/constitution.md`.)

Findings: none
