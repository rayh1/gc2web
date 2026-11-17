Started: 2026-11-17T22:33:39+01:00
Finished: 2026-11-17T22:46:51+01:00

# Build 1: private spouse

## Code change

1. `gen_site/gen_site.py`, `generate_chronology`: the spouse is looked up once. With a spouse,
   the lines are as before ("Huwelijk met <link>" and, when the spouse has a death date,
   "Overlijden partner <link>"). With None, the marriage line reads just "Huwelijk" and there is
   no partner's-death line.
2. `gen_site/model/Individual.py`, `witnessed_events`: a marriage's people are
   `[individual, spouse]`, or `[individual]` when the spouse is None.
3. Both `# type: ignore[...]` groups and the "left as it is" comments are removed. mypy passes.

## Per acceptance criterion

1. **Generation completes.** This comes from the two code fixes. All four tests in
   `gen_site/test/test_private_spouse.py` generate person pages from the fixture, and
   `test_private_spouse_appears_in_no_output` also generates the source pages and the birthday
   index. On the base code, all four fail with
   `AttributeError: 'NoneType' object has no attribute 'name'`.
2. **No trace of I2.** `test_private_spouse_appears_in_no_output` loses its `xfail` marker. Its
   body and assertions are unchanged, and it passes.
3. **I1's chronology.** The fixture `gen_site/test/fixtures/private_spouse.ged` gains
   `1 DEAT / 2 DATE 4 FEB 1890 / 2 PLAC Graauw` for I2. This is the hard case: a private partner
   with a recorded death date. The test is `test_public_spouse_keeps_marriage_without_private_partner`.
   - It parses the Chronologie section line by line (date, optional age, description).
   - It asserts that the only line dated 12-05-1875 is exactly `("12-05-1875", "Huwelijk")`.
   - It asserts that no description starts with "Overlijden partner" and no line is dated
     04-02-1890.
4. **I3's "Getuige bij" entry.** The test is `test_witness_entry_names_only_public_partner`.
   - It asserts that there is exactly one `- Huwelijk ` entry in the section, dated
     `op 12 MAY 1875`.
   - It asserts that the entry's Markdown links are exactly
     `[("Johannes Publiek", "../i1/")]`, and that any HTML `href` in it points to a source page
     (`../sN/`).
5. **One partner, no one on the other side.** The new fixture
   `gen_site/test/fixtures/single_partner.ged` has I1 Cornelis Alleen as the only partner in F1,
   married 20 JUN 1876 with public witness I3 Pieter Getuige. S1 is in it for the gedq reason
   the spec's Context gives. The test is `test_family_without_other_partner`.
   - It asserts that the only line dated 20-06-1876 on I1's page is `Huwelijk` and that there is
     no "Overlijden partner" line.
   - It asserts that I3 has one `Huwelijk` entry dated `op 20 JUN 1876` whose only person link
     is `[Cornelis Alleen](../i1/)`.
6. **Hoofman pages byte-identical to base-code output.** The test is
   `gen_site/test/test_hoofman_pages_unchanged.py::test_hoofman_pages_match_base_code`.
   - It extracts `gen_site/` at `4e2dcc27…` with `git archive` into `tmp_path`.
   - In two separate interpreters, it generates the person and source pages from the checkout's
     `gen_site/Hoofman.ged` into two `tmp_path` folders: once with the base code and once with
     this checkout's code. Nothing goes to `src/`.
   - It asserts that both runs produce the same file names (more than 300 pages) and that every
     file is byte-identical. It passes.
   - By nature, this test also passes on the base, because it compares base output with base
     output. I checked that it is able to fail: with `"Huwelijk met"` changed to
     `"Huwelijk  met"` in the new code, it failed and listed the changed pages (`I00005.md`, …).
     The code was then restored.
   - It needs `git` and the base commit, and both are in the CI image, since `.git` is in the
     build context. In a tree with no `.git` it errors in `git archive`.
   - "Every existing test still passes" is shown by the suite runs below.

## Existing tests changed

- `test_private_spouse_appears_in_no_output`: the `@pytest.mark.xfail(...)` marker is removed.
  The spec's Decisions say: "The existing test `test_private_spouse_appears_in_no_output` …
  loses its `xfail` marker and must pass; its assertions stay as they are." Its fixture gains
  I2's death date, per the same decision.
- No other existing test is touched.

## Suite runs

- Suite: `time uv run pytest gen_site/test/test_private_spouse.py gen_site/test/test_hoofman_pages_unchanged.py` (scratch copy of the base tree with the new tests and fixtures; run there by direct pytest, not `bash .devcontainer/ci.sh`) — the 4 private-spouse tests failed with AttributeError; the Hoofman test errored in `git archive` (no `.git` in the copy); with `GIT_DIR` pointed at the repo, the Hoofman test passed (base against base) — 16.9 s, then 14.5 s
- Suite: `bash .devcontainer/ci.sh` — exit 1: `ruff check` PLW1510 (`subprocess.run` without `check`) in the new `test_hoofman_pages_unchanged.py`; pytest 63 passed; npm checks, osv-scanner and mypy passed — 2m03.7s
- Suite: `bash .devcontainer/ci.sh` (after adding `check=False`) — exit 0: ruff check and format, pytest 63 passed, npm checks, osv-scanner and mypy all passed — 3m14.2s
- Suite: `python3 /workspace/.claude/skills/create-constitution/scripts/constitution-ci.py --project .` — exit 0, [C-1] PASS — 1m14.1s

## What the spec should say instead

1. **The constitution command in Context writes into `src/`.** Rule [C-1] runs
   `test_migration_contract.py -k test_private_people_are_excluded` on the host. That class's
   `setUpClass` runs `python gen_site.py Hoofman.ged`, which is `main()`. My run therefore
   rewrote these files in the real tree:
   - `src/content/entity/I00323.md`, `I00350.md` and `I00351.md`: the three place-separator pages
     that Context mentions.
   - `src/last_modified.ts`
   - `src/data/birthday-index.json`, with identical content.

   At my first command, `git status` showed nothing but `specs/private-spouse/`, so I restored
   the four changed files with `git checkout --`. The tree now differs from the base only by this
   change. Context should warn that the constitution runner (and any host `pytest` run of
   `test_migration_contract.py`, or a bare host `uv run pytest`) writes into `src/`. A clean
   `git status -- src/` afterwards, or a restore, should be part of the routine. `ci.sh` is
   unaffected because it runs in a throwaway container.
2. **Criterion 6 as a permanent test.** The test is pinned to the base commit. Any later change
   that alters the Hoofman pages on purpose will fail it and must replace or remove it. The
   test's docstring says so. The migration-contract test in this repo has the same kind of pin
   (`BASELINE_COMMIT`).
