# Review Fix Plan: gc2web gedq Migration

**Source:** create-review (spec-conformance verification)
**PRD:** specs/gc2web-gedq-migration/gc2web-gedq-migration.prd.md
**Design Document:** specs/gc2web-gedq-migration/gc2web-gedq-migration.dd.md
**Generated:** 2026-06-24T19:30:00Z
**Review scope:** eab4d3063c936fb1ba79878d24cda21b95bd5f21..working-tree
**Confirmed findings:** 1 -> 1 fix task

## Fix Tasks

- [x] #1 Remove gen_site.py behavior wrapper [AUTONOMOUS] [HIGH confidence]
  - **Finding:** [F-1] implementation deviation: `gen_site.py` still contains a behavior-level dependency-error wrapper outside the revised seam allowance.
  - **Files:**
    - `gen_site/gen_site.py` (remove the behavior-level wrapper)
    - `gen_site/model/GedcomModel.py` or `gen_site/adapter/gedq_adapter.py` (own the dependency failure exit path there if still needed)
    - `gen_site/test/test_migration_contract.py` (adjust verification if needed)
  - **Success criteria:**
    - `gen_site.py` contains only the allowed non-behavioral seam edits after the migration (obsolete import cleanup and repo-local path normalization).
    - Dependency failure exit behavior lives outside `gen_site.py`.
    - Generation still exits cleanly on missing/incompatible `gedq`.
    - PRD R-3 remains satisfied with executable evidence.
  - **Verify:** `cd /workspace/gen_site && PYTHONPATH=. python -m pytest -q test && ! rg -n 'except RuntimeError as exc|raise SystemExit\(1\) from exc' gen_site.py`
  - **Reference:** PRD [R-3], DD [AC-2], DD Verification Hook [R-3]
