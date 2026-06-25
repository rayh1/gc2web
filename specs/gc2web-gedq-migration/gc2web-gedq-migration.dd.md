---
code0_ref: eab4d3063c936fb1ba79878d24cda21b95bd5f21
depth: constraints-only
---

# Design Document: gc2web — Replace Custom GEDCOM Parser with gedq

PRD: specs/gc2web-gedq-migration/gc2web-gedq-migration.prd.md

## Codebase Analysis

Code~0~ = `eab4d30` (gc2web `main`). The GEDCOM pipeline is Python under `gen_site/`; the Astro/TS layer consumes only generated Markdown and is out of scope.

- **Parse seam.** `GedcomModel.parse_file(gedcom_file)` (`gen_site/model/GedcomModel.py:91-96`) opens the file, calls `GedcomParser().parse(stream)`, then `GedcomModel().parse_gedcom()`. `parse_gedcom()` (`:54`) fans out to `__parse_individuals/__parse_families/__parse_sources/__parse_repositories`, each iterating `GedcomParser().iterate(tag=…)` (`:24,:30,:36,:45`).
- **Model population.** Each model class exposes `parse(self, line: GedcomLine)` that walks sublines via `GedcomParser().iterate(line, …)` (e.g. `model/Individual.py:50,57,84`). These methods are the only coupling between the model classes and the custom parser.
- **Singleton + accessors.** `GedcomModel` is a singleton holding `__individual_map`, `__family_map`, `__source_map`, `__repository_map`, exposed via `.individuals`, `.sources`, `.get_individual(id)`.
- **Generators.** `gen_site.py:main()` (`:358-367`) calls `GedcomModel().parse_file(args.file)`, then `generate_individual_pages` / `generate_source_pages` iterate `GedcomModel().individuals` / `.sources` (`:337,:342`); witness rendering calls `GedcomModel().get_individual(...)` (`:116`).
- **No gedq integration exists yet** — `grep` for `subprocess|gedq|--version` in `gen_site/` returns nothing.

Implication: the adapter can replace `parse_file` + the `__parse_*` methods + each model class's `parse(line)` while populating the same singleton maps, leaving generators, accessors, and Astro untouched.

## Approach Constraints

Locked-in decisions. Everything not stated here is delegated to the builder, who follows project conventions and the PRD acceptance criteria.

- **[AC-1] Integration mechanism.** Data is sourced from gedq via CLI subprocess, JSON output only. Bulk per-kind queries — `gedq search <ged> --kind INDI`, `… --kind FAM`, `… --kind REPO`, each with `--full --json`, plus `gedq search <ged> --kind SOUR --full --json --expand cites` for documented name-citation reconstruction — parsed as JSON Lines. No per-entity CLI calls. No import of gedq's internal Python modules. (PRD R-1, R-2)
- **[AC-2] Adapter seam.** A new adapter replaces `GedcomParser` as the data source and populates the existing `GedcomModel` singleton maps (`__individual_map`, `__family_map`, `__source_map`, `__repository_map`) at the `parse_file` seam. `gen_site.py` generator behavior, Markdown output logic, `GedcomModel().individuals/.sources/.get_individual()`, and the Astro layer are not modified; limited, non-behavioral `gen_site.py` edits are allowed only when required to remove obsolete parser-only imports or normalize repo-local workspace paths. (PRD R-3)
- **[AC-3] Model construction.** The model classes (`Individual`, `Family`, `Source`, `Repository`, `EventDetail`, `Date`, `Place`, `Name`, `Note`, `Witness`, `Association`) are constructed from gedq JSON fields; their `GedcomLine`-based `parse(line)` methods are removed. Their computed properties, relationship resolution, and display formatting (`Date.pretty_str`, `Name.plain_value`, `Place` cleaning) are retained and fed gedq's raw GEDCOM date/place/name strings. (PRD R-3, R-9)
- **[AC-4] Witness/timestamp source.** Event witnesses and event timestamps are reconstructed from gedq event `notes` (the YAML-encoded blocks) — the same source the current code parses — and NOT from gedq `associations`. (PRD R-6, E-1)
- **[AC-5] gedq dependency.** gedq is a required build dependency. At generation startup the adapter parses `gedq --version` and aborts with a non-zero exit and a message naming gedq and the required version if gedq is absent or its version is `< 2.0.0` (the canonical-field JSON contract floor). There is no fallback to a custom parser. (PRD R-8) **Provisioning (done):** gedq is installed in the devcontainer from the vendored wheel `vendor/gedq-2.0.0-py3-none-any.whl` by `init.sh` (`uv tool install --force`, with `UV_TOOL_BIN_DIR=/opt/venv/bin` so the `gedq` launcher is on PATH; the tool env stays isolated from `/opt/venv`). The container's Python 3.14.5 satisfies gedq's `>=3.14` floor. The gedq CLI reference is vendored alongside at `vendor/gedq-user-manual.md`.
- **[AC-6] Parser removal.** `gen_site/parser/` is deleted and the `parse`/populate methods are removed from the model classes; no GEDCOM-tokenizing code remains. (PRD R-9)

## Technical Approach

Constraints-only depth — the constraints below bound the solution; the builder works out the implementation.

The adapter runs the four AC-1 queries once per generation (replacing `GedcomParser().parse`), parses each JSONL stream, and constructs model objects (AC-3), inserting them into the `GedcomModel` singleton maps keyed by `entity_id` (AC-2). `parse_file` is rewired to call the adapter instead of `GedcomParser`/`parse_gedcom`; the `__parse_*` methods are removed. Per-entity nested gedq fields map to model fields (confirm the exact JSON shape in-container via `gedq schema --mode person|family|source|event|note`, `gedq search --kind <K> --full --json`, and the documented `gedq source/search --expand cites` surface in `vendor/gedq-user-manual.md`): `events[]` filtered by `tag` → `birth/death/baptism(CHR)/burial(BURI)` and the `occupations/residences/facts/descriptions` lists; `husb/wife/chil` → `Family` roles; `repository_ref`/REPO `www` → `Source.repository` / `Repository.www`; source `CITES` rows are used only to recover name-specific source edges that the flat source schema does not otherwise expose; record `note` and event `notes` → `Note`/privacy/witness reconstruction (AC-4). Date/place/name strings pass through to the existing formatters unchanged.

Privacy exclusion (record `note` carrying `private: true`) and the witness/timestamp YAML reconstruction remain gc2web logic, now reading gedq's note fields rather than parsed `GedcomLine` sublines.

## Cross-Cutting Checklist

- **Dependency / stack policy** — gedq becomes a required external CLI dependency (AC-5), provisioned in the devcontainer from the vendored wheel via `init.sh` (no manual install step). Approach: startup `gedq --version` floor check. Verification hook: run generation with gedq absent → process exits non-zero naming gedq + required version (test in Testing Strategy); after a container build, `gedq --version` reports `2.0.0` on PATH.
- **Build / CI** — gedq creates a `.ladybug` cache directory beside the GEDCOM on first read (PRD E-6). Approach: add the cache path to `.gitignore`; generation tolerates a cold (first-build) or warm cache. Verification hook: `git status --porcelain` shows no `.ladybug` entry tracked; generation succeeds with the cache absent.
- **Data integrity / correctness** — output must be byte-identical to baseline (PRD R-4). Approach: the committed diff test. Verification hook: pytest asserting `diff ⊆ allowlist` (Testing Strategy).
- **Privacy** — private individuals excluded (PRD R-5). Approach: adapter drops records whose `note` carries `private: true` before populating the maps. Verification hook: assert no page is generated for a known private individual ID.
- **Error handling** — bad GEDCOM path or a non-zero gedq exit aborts generation with a clear error rather than producing partial output. Verification hook: test generation with a missing GEDCOM path and with a simulated gedq failure → non-zero exit, no partial corpus written.

Considered but not applicable: Security (input is a local, owner-supplied GEDCOM — no untrusted boundary), Performance (PRD explicitly sets no build-time budget), Internationalization, Authn/Authz, Concurrency/locking, Observability/metrics.

## Testing Strategy

- **Baseline fixture.** Capture the current `src/content/entity/` corpus as a committed baseline before any code change (the pre-migration oracle for PRD R-4).
- **Diff test (pytest).** Regenerate the corpus from a fixed test GEDCOM (`Hoofman.ged`) and compare each file to the baseline; assert every difference is on a committed allowlist file. The allowlist enumerates each intentional difference with a justification (fixed defect or approved change) and is empty by default.
- **Targeted assertions** (beyond the bulk diff):
  - R-5: no page exists for a known `private: true` individual; page count = non-private individuals + sources.
  - R-6: a known witnessed event's rendered witness block + timestamp match the baseline byte-for-byte.
  - R-7: each feature category (names + variants, sex, BIRT/DEAT/CHR/BURI, OCCU, RESI, FACT, DSCR, ASSO, FAMS/FAMC, source citation, repository URL) appears at least once in the regenerated corpus.
  - R-8: generation with gedq absent or reporting `< 2.0.0` exits non-zero with an error naming gedq and the required version; with a compatible gedq it generates.

## Verification Hooks

- **[R-1]** End-to-end generation produces the full corpus with `gen_site/parser/` removed (proves data comes from gedq). — diff test + R-9 hook.
- **[R-2]** Adapter source contains no import of gedq internals; consumed CLI surfaces are limited to documented gedq outputs: schema-described person/family/source/event/note payloads plus the documented `--expand cites` source expansion used for name-source reconstruction. — `grep` inspection + a documented-surface assertion.
- **[R-3]** `src/` shows no diff from this effort; model class public signatures are unchanged; any `gen_site.py` delta is limited to the narrow non-behavioral seam edits allowed by AC-2, with generator behavior and generated Markdown remaining unchanged. — targeted diff review + generators run unmodified.
- **[R-4]** Regenerated corpus vs committed baseline: differences ⊆ allowlist. — diff pytest.
- **[R-5]** No file for a known private ID; corpus count equals non-private individuals + sources. — targeted pytest.
- **[R-6]** Known witnessed event renders identically to baseline. — targeted pytest.
- **[R-7]** Representative pages match baseline; feature-category checklist all present. — diff + checklist pytest.
- **[R-8]** gedq absent / `< 2.0.0` → non-zero exit + naming error; compatible → proceeds. — targeted pytest.
- **[R-9]** `gen_site/parser/` absent; model classes contain no GEDCOM-line parse methods; generation succeeds. — filesystem + `grep` assertion + end-to-end run.

## Requirements Mapping

- **[R-1]** Rewire `GedcomModel.parse_file` to call the adapter; remove `__parse_*`. — `gen_site/model/GedcomModel.py`, `gen_site/adapter/` (new).
- **[R-2]** Invoke gedq by subprocess, parse JSONL, and limit any expansion use to the documented `SOUR --expand cites` surface for name-source reconstruction; no internal imports. — `gen_site/adapter/`.
- **[R-3]** Construct model objects from gedq JSON; keep public interfaces, formatting, and relationship resolution, while limiting any `gen_site.py` edits to the narrow non-behavioral seam adjustments allowed by AC-2. — `gen_site/adapter/`, `gen_site/model/*.py`, narrow `gen_site/gen_site.py` cleanup only if needed.
- **[R-4]** Diff harness + allowlist. — `gen_site/test/` (new), allowlist file.
- **[R-5]** Drop `private: true` records in the adapter. — `gen_site/adapter/`.
- **[R-6]** Reconstruct witnesses/timestamps from event `notes` YAML (AC-4). — `gen_site/adapter/`, `gen_site/model/Witness.py`, `model/EventDetail.py`.
- **[R-7]** Map all event tags + names/sex/sources/repos. — `gen_site/adapter/`, `gen_site/model/*.py`.
- **[R-8]** `gedq --version` floor check at startup; abort on absent/incompatible. — `gen_site/adapter/`, generation entry in `gen_site.py`.
- **[R-9]** Delete `gen_site/parser/`; remove model `parse(line)` methods. — `gen_site/parser/` (delete), `gen_site/model/*.py`.

## File Touchpoints

- `gen_site/adapter/` — **to be created**: gedq invocation (AC-1), JSON→model mapping (AC-3), witness/timestamp YAML reconstruction (AC-4), privacy filtering (R-5), startup version check (AC-5).
- `gen_site/model/GedcomModel.py` — `parse_file` rewired to the adapter; `__parse_*` methods removed.
- `gen_site/model/Individual.py`, `Family.py`, `Source.py`, `Repository.py`, `EventDetail.py`, `Name.py`, `Association.py`, `Note.py`, `Witness.py`, `Place.py`, `Date.py` — remove `parse(line)`; add construction-from-data; retain computed properties + formatting.
- `gen_site/parser/` (`GedcomParser.py`, `GedcomLine.py`, `GedcomLineIterator.py`, `GedcomTags.py`) — **deleted**.
- `gen_site/test/` — **to be created**: baseline corpus fixture, diff pytest + allowlist file, targeted assertions.
- `.gitignore` — add the gedq `.ladybug` cache path.
- `vendor/gedq-2.0.0-py3-none-any.whl` — vendored gedq wheel; installed by `init.sh` (`uv tool install`, launcher on `/opt/venv/bin`) so `gedq` is on PATH. (AC-5)
- `vendor/gedq-user-manual.md` — vendored gedq CLI reference (PRD References point here).
- `init.sh` / `.devcontainer/` — gedq install step + Python 3.14.5 (satisfies gedq's `>=3.14` floor). **Done.**

## Edge Case Handling

- **[E-1]** Witnesses available via both event `notes` and gedq `associations`; reconstruct from `notes` YAML only (AC-4) — no double-count, no association substitution.
- **[E-2]** Element ordering (events, children, names, occupations, residences) drives byte-identity; the adapter preserves the order the generators expect. Ordering differences surface in the diff test and are reconciled (allowlist only if intentional).
- **[E-3]** gedq passthrough/raw fields (e.g. `_SOSADABOVILLE`) and empty place segments (`", , ,"`) are handled exactly as the old code did (ignored vs rendered) — verified by the diff test.
- **[E-4]** Null/absent optionals (`publication`, `repository_ref`, missing date/place) produce no `null`/`None` text — caught by the diff test.
- **[E-5]** CONC/CONT content (long `source_text`, multi-value publication) arrives reassembled from gedq; reassembled strings verified against baseline.
- **[E-6]** gedq `.ladybug` cache is built on first read; generation succeeds cold or warm and never depends on a pre-existing cache.
