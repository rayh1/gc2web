# gen_site — GEDCOM-to-website generator (baseline PRD)

**PRD Type:** functional

<!-- Reverse-derived by extract-spec from /workspace/gc2web/gen_site at code0_ref 052cf07e7c8e85dd68f2de5d29c5c63f2ec0d365 (2026-07-07). Every requirement is code-derived, evidence-quoted, and user-confirmed. This is the baseline spec of EXISTING behavior, not a feature proposal. -->

## Context

gen_site is gc2web's static-site generator: it reads a GEDCOM file through the gedq CLI and emits Dutch-language markdown pages (Astro content collection) for every individual and source, plus a site-freshness marker. It is the core of the gc2web publishing pipeline; the Astro frontend renders its output. Companion scripts (identify_witness, match_assocs, text_comparison) support research workflows on the same model.

## Why

The family's genealogy research lives in a GEDCOM file; this generator publishes it as a browsable, cross-linked Dutch website. A baseline PRD did not exist (the code predates SDD2); this document restores the forward-pipeline anchor so future changes — including the gedq-adapter migration work — can be reviewed against explicit promises.

## Goals

- Publish every non-private individual and every source as a self-contained markdown page with stable cross-links.
- Render genealogical facts (names, events, witnesses, relationships, chronology) in Dutch with consistent formatting.
- Preserve research provenance: source references and footnotes on every fact that carries them.
- Fail loudly when the gedq toolchain is missing or incompatible.

## Non-Goals

- Rendering HTML or serving the site (Astro's job — this emits markdown content only).
- Writing or modifying the GEDCOM (read-only consumer via gedq).
- Page types beyond individual and source pages (no family, index, or place pages).
- Localization beyond Dutch.
- Incremental regeneration (every run regenerates all pages).

## Requirements

1. [R-1] The CLI MUST accept a single positional GEDCOM-file path and, per run, generate all individual pages, all source pages, and the last-modified marker.
2. [R-2] Each individual page MUST carry YAML frontmatter with: `title` (primary name + lifespan), `description` `"Individual"`, `pubDate` fixed at `"November 20 2024"` (deliberate placeholder — the Astro content schema requires the field), `lifespan` `"(startyear-endyear)"` with `?` for an unknown year, `section_order`, and — only when derivable — `birth_place`, `death_place`, `relationship_summary`, `branch`.
3. [R-3] `section_order` MUST list, in order: `identity`, `parents` (always); `relationships` (only if spouse-families exist); `siblings` (only if any); `chronology` (always); `occupations`, `facts`, `locations`, `witnessed_events` (each only if non-empty); `sources` (always); `notes` (only if any).
4. [R-4] The chronology section MUST contain: the individual's dated birth/baptism/death/burial events; parents' deaths (when dated); marriages and spouse deaths; children's births; children's and siblings' events only when they fall within the individual's own lifetime — all sorted by date, rendered `DD-MM-YYYY`, with the individual's age appended in italics when the event lies within their lifetime.
5. [R-5] Date display MUST render `?` for absent or unparseable dates, `start - end` for ranges/periods (missing endpoint → `?`), and the parsed value otherwise.
6. [R-6] Age MUST be computed as whole years at the event date (floor of days/365) and omitted (`?` in display contexts) when either date is inexact.
7. [R-7] A witness line MUST comma-join the non-empty parts: linked name when the witness xref resolves (plain name otherwise), occupation, residence, `N jaar`, relation.
8. [R-8] Place display MUST split on commas, strip whitespace per part, drop empty parts, and re-join with `, `.
9. [R-9] Gender MUST render as `Mannelijk` (M), `Vrouwelijk` (F), or `Onbekend` (other/absent).
10. [R-10] The relationship summary MUST prefer `Partner van {spouse}` (first spouse-family) over `Kind van {vader} en {moeder}` (or the single-parent variant), and be omitted when neither applies.
11. [R-11] Each source page MUST carry frontmatter (`title`, `description` `"Source"`, `pubDate` placeholder) and sections: `Archief` linking the repository's www (only when a repository exists), `Rechtstreekse Verwijzingen` listing the source's publications, and `Tekst` with the transcript (only when text exists).
12. [R-12] Footnotes MUST use markdown reference style: `[^N]` markers accumulated in page order, definitions emitted in a closing `Voetnoten` section, numbering restarting on every page.
13. [R-13] Each individual page MUST open with an ASCII tree block: parent chain (second parent joined with an `x` connector), the birth-sorted sibling group with the focus individual marked, and the focus individual's spouse-family branches (at most 2 spouse families by default).
14. [R-14] The last-modified marker MUST be a TypeScript module containing exactly `export const LAST_MODIFIED = "DD-MM-YYYY";` with the generation date.
15. [R-15] An individual whose YAML note contains `private: true` MUST be excluded from all generated output after model load.
16. [R-16] The text-comparison tool MUST report CER, WER, and Levenshtein distance between a reference file and each candidate file, computed on normalized text (lowercased, runs of whitespace collapsed to single spaces).
17. [R-17] The identify_witness script MUST propose individual matches for unnamed witnesses using Dutch relation keywords and individual properties, skipping witnesses already identified.
18. [R-18] The match_assocs script MUST match associations to event witnesses by xref with ±1-year age tolerance, using the rel_type mapping `@#INDI:BIRT@`→birth, `@#INDI:DEAT@`→death, `@#INDI:CHR@`→baptism, and report associations without a matching witness.
19. [R-19] The first NAME occurrence MUST be the primary name; the plain form strips GEDCOM slashes; additional occurrences MUST be listed under `Alternatieve namen` with their own footnotes/source links.
20. [R-20] The generator MUST require gedq ≥ 2.0.0 and abort the run with a readable error on a missing binary, a failing `gedq --version` call, or a lower version.
21. [R-21] The `branch` frontmatter field MUST be the last space-separated token of the primary name (omitted when no name).
22. [R-22] The `Getuige bij` section MUST list events where the individual is a witness, labeled `Geboorte`/`Overlijden`/`Doop`/`Begrafenis`/`Huwelijk` (marriage rows naming both spouses), deduplicated per event and sorted by date.
23. [R-23] Life anchors MUST fall back: start of life = birth else baptism; end of life = death else burial — used for lifespan, ages, and chronology filtering.
24. [R-24] Source references on fact lines MUST render as superscript HTML anchors (`:link:` icon, source-title tooltip) linking the source's page.

## Acceptance Criteria

- [R-1] Running `gen_site.py <ged>` on a fixture produces one `{xref_id}.md` per non-private individual, one per source, and the marker file; no other page types.
- [R-2]/[R-3] A generated page for a fixture individual with spouse and siblings contains all conditional frontmatter keys and the full `section_order`; an isolated individual's page omits `relationships`/`siblings` and the conditional keys.
- [R-4] A child who died after the individual's death does not appear as a chronology death entry; a parent's death after the individual's death does; every line matches `- DD-MM-YYYY…`.
- [R-5]/[R-6] Fixture dates `ABT 1850`, `BET 1850 AND 1852`, empty → rendered per rule; an event age for an exact birth+event pair equals floor(days/365); inexact birth → age omitted.
- [R-7] A witness with xref renders a markdown link; without xref renders plain text; empty fields produce no dangling commas.
- [R-8]–[R-10] Direct unit assertions on `place_summary`, `gender_str`, `relationship_summary_str` (spouse present → `Partner van …` even when parents exist).
- [R-11] A source with repository + text renders all three sections; without them renders only `Rechtstreekse Verwijzingen`.
- [R-12] Two consecutive pages both start footnotes at `[^1]`; every marker has a matching definition in `Voetnoten`.
- [R-13] Tree block for a fixture with 2 parents, 3 siblings, 3 spouse-families shows the `x` connector, birth-sorted siblings, focus marking, and exactly 2 family branches.
- [R-14] The marker file content matches `^export const LAST_MODIFIED = "\d{2}-\d{2}-\d{4}";\n$`.
- [R-15] A fixture individual with a `private: true` YAML note yields no page and appears in no site output.
- [R-16] Known reference/candidate pair yields hand-computed CER/WER/Levenshtein values.
- [R-17]/[R-18] Fixture with an unnamed witness + matching association: identify_witness proposes the match; match_assocs accepts age ±1 and reports the unmatched remainder.
- [R-19] A two-NAME fixture lists the second under `Alternatieve namen`; `/Surname/` renders without slashes.
- [R-20] With gedq absent (PATH manipulation) or a stubbed `--version` of `1.9.0`, the run exits non-zero with a message naming the required version.
- [R-21]–[R-24] Direct assertions on branch token, `Getuige bij` dedup/sort/labels, baptism-fallback lifespan, and the `<sup><a …>` source-link markup.

## Edge Cases

1. [E-1] Undated marriage in a spouse-family: the chronology event receives the minimum date and sorts first, rendering `01-01-0001` — current behavior, flagged for review rather than promised.
2. [E-2] Links to excluded (private) individuals: family structures may still reference an excluded person (child/spouse/witness lists); witness rendering degrades to plain name, but `individual_link` from a family context may emit a link to a nonexistent page. Unverified against a fixture — verify before relying on privacy completeness.
3. [E-3] An individual with neither birth/baptism nor death/burial dates: lifespan renders `(?-?)`; lifetime filtering excludes all sibling/child events (is_in_lifetime requires both anchors).
4. [E-4] Names without spaces (single token): branch equals the whole name.
5. [E-5] A witness with an xref that no longer resolves (e.g. privacy-excluded): rendered as plain name via the resolution guard.

## Unknowns & Questions

None. ([Q]s raised during derivation were resolved at confirmation: the `pubDate` constant is a deliberate placeholder; the death-line wording is specified as intended, see [K-1].)

## Risks

1. [K-1] Known code-vs-PRD divergence at baseline: the death line currently renders `oud N jaar jaar` (`gen_site.py:258` appends ` jaar` after `age_str`, which already ends in `jaar`). [R-4]/[R-6] promise the intended single-`jaar` wording; the code needs a one-line fix to conform.
2. [K-2] The gedq-adapter migration (separate effort, `specs/gc2web-gedq-migration/`) changes the ingest layer beneath every requirement here; byte-level output parity is tracked there, but any adapter change should be reviewed against this PRD's formatting promises.
3. [K-3] `pubDate` is a fixed constant; if the Astro frontend ever sorts or displays by it, all pages tie.

## References

- Derivation: extract-spec `--from-code`, code0_ref `052cf07e7c8e85dd68f2de5d29c5c63f2ec0d365`, ledger 38 candidates → 24 promoted / 10 locked (DD) / 4 consolidated / 2 [Q] resolved.
- Companion DD: `specs/gen-site/gen-site.dd.md` (constraints-only, written by create-dd).
- Related effort specs: `specs/ascii-tree-pages/` (R-13's originating feature spec), `specs/gc2web-gedq-migration/`.
