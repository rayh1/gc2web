Started: 2026-11-17T22:52:29+01:00
Finished: 2026-11-17T22:55:09+01:00

# Build 2: private spouse (fix pass)

This pass carries out the one decision the user added after build 1: "Criterion 6 is checked by the
reviewer's own comparison for this change, not by a permanent test … `gen_site/test/test_hoofman_pages_unchanged.py`
from build 1 is deleted." `spec.md` and `approved.md` are identical. Build 1's other changes cover
every remaining criterion and Decision, so nothing else was left undone.

## Change in this pass

- Deleted `gen_site/test/test_hoofman_pages_unchanged.py`. Nothing else in the repository referred
  to it: a grep found it only in this spec folder.
- No code, fixture or other test changed. The code change from build 1 stands as `01-build.md`
  describes it.

## Per acceptance criterion

1. **Generation completes.** No change in this pass. All four tests in
   `gen_site/test/test_private_spouse.py` cover it, as in build 1.
2. **No trace of I2.** No change. `test_private_spouse_appears_in_no_output` (no `xfail`)
   covers it.
3. **I1's chronology.** No change. `test_public_spouse_keeps_marriage_without_private_partner`
   covers it, using I2's recorded death date 4 FEB 1890 in the fixture.
4. **I3's "Getuige bij" entry.** No change. `test_witness_entry_names_only_public_partner`
   covers it.
5. **One partner, no one on the other side.** No change. `test_family_without_other_partner`
   covers it with `gen_site/test/fixtures/single_partner.ged`.
6. **Hoofman pages byte-identical to base-code output.** No permanent test covers this now. Per
   the new Decision, the reviewer checks it with its own comparison. The code that criterion 6
   judges is the same as in build 1. Build 1's comparison of base and new code passed, and was
   shown able to fail. "Every existing test still passes" is shown by the suite run below.

## Existing tests changed

- `gen_site/test/test_hoofman_pages_unchanged.py` is deleted. It was a new test from build 1, not
  a test that exists at the base. Spec text: "`gen_site/test/test_hoofman_pages_unchanged.py` from
  build 1 is deleted."
- No test that exists at the base was changed in this pass. Build 1's removal of the `xfail`
  marker from `test_private_spouse_appears_in_no_output` stands.

## Suite runs

Context names no fast part of the suite, so I ran the whole suite.

- Suite: `time bash .devcontainer/ci.sh` — exit 0. ruff check and format passed; pytest 62 passed
  (63 in build 1, minus the deleted test); the npm checks (6 vitest, 30 Playwright), both
  osv-scanner scans and mypy also passed — 1m42.8s
- Suite: `time python3 /workspace/.claude/skills/create-constitution/scripts/constitution-ci.py --project .`
  — exit 0, [C-1] PASS — 30.7s

The constitution run rewrote these files, as Context warns it does:
- `src/content/entity/I00323.md`
- `src/content/entity/I00350.md`
- `src/content/entity/I00351.md`
- `src/last_modified.ts`

I restored them with `git checkout -- src/`. Afterwards `git status` shows only this change: the
four modified files under `gen_site/`, the untracked `gen_site/test/fixtures/single_partner.ged`,
and `specs/private-spouse/`.

## What the spec should say instead

Nothing.
