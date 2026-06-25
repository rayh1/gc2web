# gc2web: Replace Custom GEDCOM Parser with gedq

## PRD Type

technical

## Context

gc2web generates a static genealogy website from a GEDCOM file. The GEDCOM handling is entirely Python and lives in `gen_site/`; the Astro/TypeScript layer never touches GEDCOM and consumes only generated Markdown. The current pipeline is:

1. `gen_site/parser/` — a hand-written GEDCOM parser (`GedcomParser`, `GedcomLine`, `GedcomLineIterator`, `GedcomTags`) that tokenizes raw GEDCOM lines into a tree.
2. `gen_site/model/` — typed model classes (`Individual`, `Family`, `Source`, `Repository`, `EventDetail`, `Date`, `Place`, `Name`, `Note`, `Witness`, `Association`) whose `parse`/populate methods build objects from that tree.
3. `gen_site/gen_site.py` — Markdown generators that walk the model and write `src/content/entity/*.md`.
4. Astro — renders the Markdown to HTML.

A separate, mature project, **gedq** (a GEDCOM query CLI, v2.0.0), already parses GEDCOM and exposes the same data through a stable, schema-documented JSON contract. A spike against the project's GEDCOM (`gen_site/Hoofman.ged`: 277 individuals, 97 families, 460 sources) confirmed gedq's JSON output exposes every feature gc2web currently interprets, returns raw GEDCOM date/place/name strings (so existing display formatting is reusable as-is), and preserves raw note text and repository URLs.

## Problem

gc2web maintains a bespoke GEDCOM parser and interpretation layer that duplicates work gedq already does correctly and with validation. The custom parser is an ongoing maintenance burden and a second, divergent implementation of GEDCOM semantics. This effort replaces the custom parsing and tree-building with gedq as the data source, while leaving the generated website unchanged.

## Goals

- Make gedq the sole source of GEDCOM-derived data for site generation.
- Remove the custom GEDCOM parser and tree-building code from gc2web.
- Keep the generated website unchanged: regenerated Markdown is byte-identical to today's output except for an explicitly documented, justified set of differences.
- Preserve gc2web's data model interfaces and Markdown generators so the change is confined to the data-acquisition layer.

## Non-Goals

- Any change to gedq. This effort treats gedq as a fixed, external dependency.
- Any change to `gen_site.py`'s Markdown generators or to the Astro/TypeScript layer.
- Adding, removing, or restyling website content, pages, or features.
- Replacing or redesigning the gc2web model classes (`Individual`, `Family`, etc.) — their public interfaces are preserved.
- A build-time performance budget — generation speed is explicitly not constrained by this PRD.
- Keeping the old parser available as a runtime fallback.

## Requirements

1. [R-1] Site generation sources all GEDCOM-derived entity data from gedq. No custom GEDCOM line/tree parser participates in generation.
2. [R-2] The integration consumes only gedq's documented, stable CLI JSON output contract, not gedq's internal Python modules. Output correctness depends only on documented gedq output surfaces: the schema-described person/family/source/event/note payloads and any explicitly documented JSON expansions required for parity, currently `--expand cites` for source/name citation reconstruction.
3. [R-3] The adapter populates gc2web's existing model objects (`Individual`, `Family`, `Source`, `Repository`, `EventDetail`, `Date`, `Place`, `Name`, `Note`, `Witness`, `Association`) without changing their public interfaces. The Astro layer requires no changes. `gen_site.py` generator behavior and generated Markdown output require no changes, but limited non-behavioral `gen_site.py` edits are allowed when required to remove obsolete parser-only imports or normalize repo-local workspace paths.
4. [R-4] For a given GEDCOM, the regenerated `src/content/entity/*.md` corpus is byte-for-byte identical to the pre-migration output, except for entries on a documented allowlist. Every allowlist entry carries a written justification classifying it as a fixed defect or an approved intentional change.
5. [R-5] Privacy exclusion is preserved: an individual carrying the `private: true` note is excluded from generated output exactly as in the pre-migration behavior.
6. [R-6] Event witnesses and event timestamps render identically to the pre-migration output, derived from the same underlying source data (the YAML-encoded note blocks), now read via gedq's note fields.
7. [R-7] Every GEDCOM feature gc2web currently interprets remains represented after the migration: multiple names with variants, sex, birth, death, baptism (CHR), burial (BURI), occupations (OCCU), residences (RESI), facts (FACT), descriptions (DSCR), associations (ASSO with role), family relationships (husband/wife/children), marriage, record-level and event-level source citations, repositories including repository URL, and notes.
8. [R-8] gedq is a required, version-checked build dependency. Before generating, the generator verifies gedq is present and reports a version compatible with the JSON contract it relies on; if gedq is absent or its version is incompatible, generation aborts with a non-zero exit and an error message naming the dependency and the required version. There is no fallback to a custom parser.
9. [R-9] The custom parser is removed: `gen_site/parser/` is deleted and the GEDCOM-line parse/populate methods are removed from the model classes. No dead GEDCOM-tokenizing code remains in the repository.

## Acceptance Criteria

- [R-1] Running the generation step against the project GEDCOM produces the full entity corpus, and the generation entry path obtains its data from gedq (verified by R-9's absence of any parser module plus an end-to-end run that succeeds with `gen_site/parser/` removed).
- [R-2] The adapter contains no `import` of gedq's internal modules (verified by inspection / grep); the JSON it consumes is limited to gedq's documented CLI output surfaces: the schemas emitted by `gedq schema --mode person|family|source|event|note` plus the documented `--expand cites` source expansion used for name-source reconstruction.
- [R-3] `src/` (Astro) has zero diff attributable to this effort; the model classes' public method/attribute signatures are unchanged; and any `gen_site.py` diff is limited to the allowed non-behavioral cleanup class while the generators still run unmodified and produce the same Markdown output.
- [R-4] A diff test regenerates the entire `src/content/entity/` corpus from the same GEDCOM and compares it to a captured pre-migration baseline; the comparison reports no differences outside the allowlist file, and the allowlist file enumerates every remaining difference with a justification. An empty allowlist is the pass-by-default state.
- [R-5] No `.md` page is generated for any individual whose record carries `private: true`; the generated page count equals (non-private individuals + sources), and a known private individual ID has no corresponding file. (Subsumed by the R-4 diff, plus this targeted assertion.)
- [R-6] For at least one known event with witnesses and a timestamp, the rendered witness block (name, occupation, age, relation as applicable) and timestamp match the baseline byte-for-byte.
- [R-7] For a representative individual exercising every feature category in [R-7] and a source whose repository has a URL, the generated pages match the baseline; additionally, a checklist assertion confirms each feature category appears at least once across the regenerated corpus.
- [R-8] Invoking generation with gedq absent or at an incompatible version aborts with a non-zero exit and an error naming the missing/incompatible dependency and the required version; invoking it with a compatible gedq proceeds to generate.
- [R-9] `gen_site/parser/` does not exist after the change; the model classes contain no GEDCOM-line parse/populate methods; the project generates the corpus successfully without them.

## Edge Cases

- [E-1] Witness data is available in gedq two ways — event-level note text (the YAML blocks) and `associations` entries with role `Getuige` (witness). The byte-identical bar (R-4) requires the adapter to reconstruct witnesses from the same source the current code uses (the YAML notes) and not to substitute or double-count the association-based representation.
- [E-2] Byte-identical output depends on the ordering of repeated elements (events, children, names, occupations, residences). If gedq emits these in a different order than the old parser, generated lists differ. The adapter must reproduce the ordering the generators expect; any ordering difference reaches output only as a justified allowlist entry.
- [E-3] gedq passes through raw/non-standard fields (e.g. `_SOSADABOVILLE`) and empty place segments (e.g. `", , , ,"`). The adapter must treat these exactly as the old code did (ignore vs. render) so they do not leak into or vanish from output.
- [E-4] Records with missing optional fields (null `publication`, null `repository_ref`, absent date or place) must produce the same output as before, with no `null`/`None` text leaking into Markdown.
- [E-5] Multi-line / continuation content (CONC/CONT) — long `source_text`, multi-value publication — must reassemble into the same strings the old parser produced.
- [E-6] gedq builds a derived cache (`.ladybug`) beside the GEDCOM on first read. Generation must succeed whether the cache is cold (first build) or warm, and must not depend on a pre-existing cache.

## Unknowns & Questions

None.

## Risks

- [K-1] gedq field-contract drift: a future gedq version could rename or restructure JSON fields and silently change gc2web's output. Mitigated by R-8 (startup version check), R-2 (reliance on the documented contract only), and R-4 (diff test catches output changes).
- [K-2] Hidden semantic differences between the custom parser and gedq (date normalization, place cleaning, deduplication) could surface as a large diff that inflates the allowlist and hides real regressions. Mitigated by triaging every diff; a large or unexplained diff blocks the migration rather than being allowlisted wholesale.
- [K-3] Witness/timestamp reconstruction (E-1) is the only non-mechanical mapping; an error here produces subtle, hard-to-spot content defects. Mitigated by the targeted R-6 assertion in addition to the bulk diff.
- [K-4] Coupling gc2web's build to gedq adds an external, actively-developed dependency. Accepted: the same owner maintains both projects.

## Assumptions

- gedq v2.0.0 (the canonical-field JSON contract) is installed and invocable at build time.
- The pre-migration Markdown corpus is captured as the diff baseline before any code change.
- gedq returns raw GEDCOM date/place/name strings (confirmed against `gen_site/Hoofman.ged`), so gc2web's existing `Date`, `Place`, and `Name` formatting is reused unchanged.
- Families produce no standalone pages; FAM data feeds individual pages (page count = non-private individuals + sources).

## References

- gedq field mapping and feature coverage are verifiable in-container: `gedq schema --mode person|family|source|event|note` for the JSON contract, and bulk `gedq search --kind INDI|FAM|SOUR|REPO --full --json` against `gen_site/Hoofman.ged` for complete records; see `vendor/gedq-user-manual.md`.
- gedq JSON schema: `gedq schema --mode person|family|source|event|note`; documented CLI expansions including `--expand cites` are described in `vendor/gedq-user-manual.md`.
- gc2web model and generators: `gen_site/model/`, `gen_site/gen_site.py`.
