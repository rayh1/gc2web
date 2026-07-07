---
code0_ref: 052cf07e7c8e85dd68f2de5d29c5c63f2ec0d365
depth: constraints-only
---

# gen_site — GEDCOM-to-website generator (baseline PRD) Design Document

**PRD:** specs/gen-site/gen-site.prd.md

<!-- Reverse-derived baseline (extract-spec, 2026-07-07): the code exists; this DD locks the load-bearing decisions AS constraints (state-as-baseline). Everything not listed is delegated to codebase conventions. -->

## Codebase Analysis

Code~0~ (`052cf07e`) is a working generator of ~3,900 Python lines in five layers: `gen_site.py` (entrypoint + all page rendering), `adapter/gedq_adapter.py` (gedq CLI subprocess ingest → domain objects), `model/` (Individual/Family/Source/Repository/EventDetail/Date/Name/Note/Witness/Association + GedcomModel), `util/` (AsciiTreeRenderer, singleton), `scripts/` (identify_witness, match_assocs) and `text_comparison.py`. Rendering is markdown-with-YAML-frontmatter into an Astro content collection; all text output is Dutch. The adapter replaced a custom GEDCOM parser (see `specs/gc2web-gedq-migration/`); byte-level output parity with the legacy parser is an active concern for ingest-layer constraints. Structural map: no `ARCHITECTURE.md` exists for this repo — none referenced.

## Technical Approach

Constraints-only. The ten locked constraints below bind any future change; silence on everything else is delegation to codebase rules and general design practice.

1. **[D-1] Output locations.** Individual AND source pages write to `/workspace/src/content/entity/{xref_id}.md`; the freshness marker to `/workspace/src/last_modified.ts`. The Astro content collection depends on these exact paths. (`gen_site.py:19,22,397-404`)
2. **[D-2] In-memory singleton model.** `GedcomModel` is a process-wide singleton holding the full dataset (individual/family/source/repository maps + relationship caches); reload only via `parse_file` → `clear`. (`model/GedcomModel.py:17-18`)
3. **[D-3] gedq subprocess ingest contract.** `load_dataset` fetches four record kinds — `INDI`, `FAM`, `SOUR --expand cites`, `REPO` — as JSON from the gedq CLI, gated on gedq ≥ 2.0.0. The adapter is wholly dependent on gedq's documented JSON schema. (`adapter/gedq_adapter.py:83-92`)
4. **[D-4] Witness/timestamp data as YAML-in-NOTEs.** Witness lists and timestamps live as YAML embedded in GEDCOM event NOTEs; the FIRST note carrying the key wins. Migration watch-item: any change to note round-tripping breaks witness data. (`model/EventDetail.py:21-37`)
5. **[D-5] Lowercase relative URL scheme.** All entity links are `../{xref_id.lower()}/`; the frontend must serve lowercase routes. (`gen_site.py:46-54`)
6. **[D-6] Association role vocabulary.** Roles split on the first space into `rel_desc` + `rel_type` (e.g. `@#INDI:BIRT@`); scripts rely on this vocabulary. (`adapter/gedq_adapter.py:282-293`)
7. **[D-7] Single- vs multi-event tags.** `BIRT`/`DEAT`/`CHR`/`BURI` occupy one slot (later same-tag occurrences overwrite); `OCCU`/`RESI`/`FACT`/`DSCR` append to lists. (`adapter/gedq_adapter.py:27-40`)
8. **[D-8] Line-ending normalization.** Multiline text normalizes to `\r\n` on ingest. Byte-parity-sensitive (migration audit). (`adapter/gedq_adapter.py:377-380`)
9. **[D-9] Note deduplication.** Notes dedupe by `(value, line_num)`; footnote and note counts depend on it. (`adapter/gedq_adapter.py:391-400`)
10. **[D-10] Date-parser precedence.** Parsers try in fixed order — period (`FROM`/`TO`), range (`BET`), approximated (`ABT`/`CAL`/`EST`), interpreted (`INT`), simple — first match wins; display and sorting semantics depend on the order. (`model/Date.py` `PARSERS`)

## Requirements Mapping

Baseline form: each requirement is already implemented at the cited location; the mapping anchors future change review.

| Req | Implemented at |
|---|---|
| [R-1] | `gen_site.py:419-429` `main()` → `generate_individual_pages` / `generate_source_pages` / `generate_last_modified` |
| [R-2] | `gen_site.py:221-237` frontmatter block in `generate_individual_page` |
| [R-3] | `gen_site.py:199-215` `section_order` assembly |
| [R-4] | `gen_site.py:156-191` `generate_chronology` (+ `is_in_lifetime:86-92`) |
| [R-5] | `model/Date.py` `pretty_str` |
| [R-6] | `model/Individual.py` `age` |
| [R-7] | `gen_site.py:144-154` `witness_str` |
| [R-8] | `gen_site.py:127-134` `place_summary` |
| [R-9] | `gen_site.py:136-142` `gender_str` |
| [R-10] | `gen_site.py:112-125` `relationship_summary_str` |
| [R-11] | `gen_site.py:365-395` `generate_source_page` |
| [R-12] | `model/Footnote.py` `add`/`gen` + `gen_site.py:355-358` |
| [R-13] | `util/AsciiTreeRenderer.py` `render_ascii_tree` (default `max_spouse_families=2`) |
| [R-14] | `gen_site.py:406-417` `generate_last_modified` |
| [R-15] | `model/GedcomModel.py` `__exclude_privates` (called from `parse_file`) |
| [R-16] | `text_comparison.py` `normalize_text`/`calculate_cer`/`calculate_wer`/`levenshtein_distance` |
| [R-17] | `scripts/identify_witness.py` `identify_witnesses` |
| [R-18] | `scripts/match_assocs.py` `match_assocs` (rel_type mapping in header comments) |
| [R-19] | `model/Name.py` `plain_value` + `gen_site.py:265-268` Alternatieve namen |
| [R-20] | `adapter/gedq_adapter.py:59-80` `ensure_gedq_compatible` + `model/GedcomModel.py` `parse_file` SystemExit |
| [R-21] | `gen_site.py:106-110` `branch_str` |
| [R-22] | `model/Individual.py` `witnessed_events` + `gen_site.py:335-340` |
| [R-23] | `model/Individual.py` `start_life`/`end_life` |
| [R-24] | `gen_site.py:65-71` `sources_str` |

## Verification Hooks

Proved by the fixture/unit assertions in the PRD's Acceptance Criteria, one per requirement: [R-1] page-count run on a fixture GEDCOM; [R-2]/[R-3] frontmatter + section_order assertions for connected vs isolated fixtures; [R-4] chronology filter/order/format assertions; [R-5]/[R-6] date + age unit tests; [R-7]–[R-10] direct unit assertions on the four formatters; [R-11] source-page section assertions; [R-12] two-page footnote-restart assertion; [R-13] tree-shape assertion; [R-14] marker regex; [R-15] private-fixture absence sweep; [R-16] hand-computed metric pair; [R-17]/[R-18] witness-match fixtures; [R-19] two-NAME fixture; [R-20] PATH/stub version-gate tests (exit non-zero, message names required version); [R-21]–[R-24] direct assertions (branch token, Getuige-bij dedup/sort, baptism-fallback lifespan, `<sup><a>` markup). No test suite currently encodes these — they are the verification contract for future change, not a claim that automated tests exist at Code~0~.

## Cross-Cutting Checklist

- **Byte-parity sensitivity (D-8, D-9, D-10):** any ingest-layer change must run the migration parity audit (`specs/gc2web-gedq-migration/page-diff-analysis.md` methodology) before landing.
- **Privacy completeness (R-15):** privacy exclusion happens at model level; PRD [E-2] flags that family-context links to excluded individuals are unverified — check on any privacy-adjacent change.
- **Dutch-language consistency:** all user-visible strings are Dutch; new output goes through the same vocabulary (labels like `Geboorte`/`Overlijden` are load-bearing for R-22).
- **Toolchain gate (D-3):** any gedq upgrade must re-check the version gate and the four-kind JSON contract.

## File Touchpoints

Baseline (no files to be created by this DD): `gen_site/gen_site.py` · `gen_site/adapter/gedq_adapter.py` · `gen_site/model/*.py` · `gen_site/util/AsciiTreeRenderer.py` · `gen_site/scripts/identify_witness.py` · `gen_site/scripts/match_assocs.py` · `gen_site/text_comparison.py` · output tree `/workspace/src/content/entity/` + `/workspace/src/last_modified.ts`.
