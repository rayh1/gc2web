# Review Fix Plan: Birthday-today block on hoofman.nl

Source: create-review (spec-conformance verification)
Change-request spec: specs/birthday-today/birthday-today.cr.md
Generated: 2026-07-28T15:23:29Z
Review scope: 72a52cd6fbac30fb0994230dee6e69689002c7df..working tree
Confirmed findings: 4 → 1 fix task (3 route upstream to `create-cr revise`)

Depth: **light** (CR mode). Apply this plan in place with the coding assistant —
do NOT route it through `execute-plan`; the light path has no plan-execute stage.

## Fix Tasks

- [x] #1 Derive `gen_site.py`'s remaining output paths from `REPO_ROOT` [REVIEW] [MEDIUM confidence]
  **APPLIED 2026-07-28.** `REPO_ROOT` moved above the block; `CONTENT_DIR` and
  `LAST_MODIFIED_FILE` now derive from it. Verified: all three output paths resolve
  inside the checkout; 7 sampled entity pages regenerate byte-identical to the committed
  ones; `pytest test/` 70 passed / 9 pre-existing errors — unchanged from before the fix.
  Finding ref: [F-4]
  Files: gen_site/gen_site.py (modify, lines 21-30)
  Problem: this change added `REPO_ROOT: Path = Path(__file__).resolve().parent.parent`
    and correctly derived `BIRTHDAY_INDEX_FILE` from it, while leaving the adjacent
    `CONTENT_DIR: Path = Path("/workspace/src/content/entity")` and
    `LAST_MODIFIED_FILE = "/workspace/src/last_modified.ts"` hardcoded. The repo is at
    `/workspace/gc2web`, so running `gen_site.py` as shipped writes 829 generated files
    outside the checkout. Two adjacent constants in one file now disagree about how a
    path is resolved.
  Success criteria: `CONTENT_DIR` and `LAST_MODIFIED_FILE` are both derived from
    `REPO_ROOT`; `python gen_site.py Hoofman.ged` writes every artifact inside the
    checkout and nothing under `/workspace/src`; the generated entity pages remain
    byte-identical to the committed ones in `src/content/entity/`.
  Verify: `bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest test/ -q'`
    plus a `gen_site.py` run confirming no writes land outside the repo.
  Reference: [F-4]; no `[R-*]` fails because of this — it is pre-existing scope the
    delta made internally inconsistent.

## Observed, not actioned

Two further members of the same stale-path family were deliberately left out of this
plan (user decision, 2026-07-28 — fix scope limited to `gen_site.py`):

- `gen_site/test/test_ascii_tree_generation.py:12` — hardcodes
  `/workspace/gen_site/Hoofman.ged`; the test errors. Reproduced at baseline `924acd4`.
- `gen_site/test/test_migration_contract.py:14` — `WORKSPACE_DIR = Path("/workspace")`;
  8 tests error, including `test_private_people_are_excluded`, which means the manual
  `private: true` flag is currently unguarded. Already recorded in
  `specs/constitution.md`'s 2026-07-26 revision notes.

## Routed upstream — `create-cr revise`

Not code fixes. See the review summary for the full evidence.

- **[F-1]** § 3 Delegated says the Dutch wording is the builder's choice; `[R-3]`,
  `[R-4]` and `[R-5]` each fix their string verbatim. The delegation was closed by the
  user-confirmed worked examples (EL-31/32/33) and should move to Locked, as the
  ordering delegation already did.
- **[F-2]** `<!-- observed: -->` markers pin counts without a commit anchor. The
  `[R-10]` marker's "170-entry gedq-realistic pool" is `5042ca9`-era; the current
  measurement is 171, and only § 4's prose (which does anchor, to `de5371a`) resolves
  whether that is drift.
- **[F-3]** The § 4 invariant "No individual for whom `may_appear_in_aggregate` returns
  False appears in any shipped artifact" is literally false for the site as shipped:
  `I00122`, `I00323` and `I00324` are withheld and each has a committed entity page and
  a built `dist/entity/…` route. `[C-1]` deliberately exempts those. Scope the invariant
  to newly added aggregate output. Also a **capture-rule candidate** — it is the review's
  one untagged cross-cutting obligation (`R-prose-1`).
