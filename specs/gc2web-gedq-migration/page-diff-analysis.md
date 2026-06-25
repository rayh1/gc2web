# Generated Page Diff Analysis

This report compares the committed generated pages in `src/content/entity/` with the current uncommitted regenerated pages.

PlantUML image URL changes are intentionally ignored here. The classification below focuses only on content differences that affect the rendered page text.

## Cause Codes

- `A` — **Single-child family omission**: the adapter reads lean gedq `FAM.chil` as a scalar string in some records (for example `"chil":"I00006"`) but `build_families()` currently does `list(record.get("chil", []))`, which turns a single child ID into a character list instead of `['I00006']`. This removes the child from `Family.children`, which then removes the `Kind ...` line, the corresponding chronology birth line, and sometimes a child-linked source from `Bronnen lijst`.
- `B` — **Name-source ordering/grouping drift**: name citations are reconstructed from gedq `SOUR --expand cites` / `CITES` by `_build_name_source_map()` using `(entity_id, name value)` grouping. That preserves source membership but not the old per-occurrence ordering/grouping semantics of repeated `NAME` structures, so `Naam:` and `Alternatieve namen:` lines may contain the same sources in a different order or grouped under a different repeated name occurrence.
- `C` — **Name-attached footnote loss**: gedq's public JSON does not preserve per-`NAME` note attachment with enough fidelity to reproduce some old name footnotes. This shows up as a missing footnote block tied to a name variant or primary name.
- `D` — **Record-level source drop**: the adapter reads lean gedq `INDI.source_ids` as iterable without normalizing scalar-string cases (for example `"source_ids":"S00012"`). That can drop a record-level source from `individual.sources`, which then removes one entry from `Bronnen lijst`.
- `E` — **Source-order-only drift**: the source set is unchanged, but `individual.all_sources()` sees a different first-seen order than the committed baseline, so `Bronnen lijst` is reordered.
- `F` — **Placeholder chronology year formatting drift**: unknown-year chronology entries that used to render as `01-01-1` now render as `01-01-0001`. This is a residual baseline formatting mismatch, not a name-projection problem.

## Current Cluster Summary

With gedq `2.0.1` and the adapter consuming the documented `names[]` occurrence payload, the `B` and `C` residuals are gone. The remaining residual diff set is now **28 files**, all in one separate approved class.

- `A` Single-child family omission: fixed in the adapter
- `B` Name-source ordering/grouping drift: fixed upstream by `names[].source_ids` plus adapter adoption
- `C` Name-attached footnote loss: fixed upstream by `names[].notes` plus adapter adoption
- `D` Record-level source drop: fixed in the adapter
- `F` Placeholder chronology year formatting drift: 28 files remain allowlisted

The generated corpus no longer has any name-projection residuals. The only current page-content allowlist is the placeholder chronology year formatting class.

## Current Per-File Classification

There are no remaining `B` or `C` files. All current generated-page content diffs fall under `F` and are listed in `gen_site/test/migration_allowlist.json`.

## Best Next Fix Order

1. Keep the adapter on gedq `names[]` as the primary name surface.
2. Keep the migration allowlist narrowed to the 28 approved `F` files so any reappearance of `B` or `C` fails the contract test as a real regression.
3. Decide separately whether the `01-01-1` to `01-01-0001` chronology formatting difference should stay approved or should be normalized back to the old baseline.

## Current High-Confidence Evidence Anchors

- `gedq schema --mode person` in `2.0.1`: exposes documented `names[]` occurrences with `name_index`, `value`, `source_ids`, `notes`, `note_refs`, and `src`.
- `gedq search gen_site/Hoofman.ged --kind INDI --full --json --with-src` for `I00014`: now exposes the primary-name note text directly under `names[0].notes` and preserves ordered per-name `source_ids`.
- `gen_site/adapter/gedq_adapter.py`: `_build_names(...)` now consumes `record["names"]` first and falls back to the older `name_variants` plus source `CITES` reconstruction only when `names[]` is absent.
- `gen_site/test/test_migration_contract.py`: the only remaining allowlisted page diffs are the 28 placeholder chronology year-formatting files.

## Historical Note

The appendices below remain useful because they document the failure modes discovered during migration. `A` and `D` were fixed in the adapter, and `B` and `C` were resolved once gedq `2.0.1` published `names[]` with per-occurrence sources and notes. The remaining `F` class is separate and still current.

## Appendix A: Single-Child Family Omission

### Beginner explanation

Some family records in gedq say "this family has one child" using a single string value, for example:

```json
"chil": "I00006"
```

Our adapter currently does this:

```python
list(record.get("chil", []))
```

If `chil` is already a list, that works.
If `chil` is a single string like `"I00006"`, Python turns it into a list of characters:

```python
['I', '0', '0', '0', '0', '6']
```

That is the bug.

Later, the code tries to look up children by ID. It looks for child IDs like `I00006`, but instead it gets `I`, `0`, `0`, `0`, `0`, `6`. Those are not real person IDs, so the child disappears.

### What that looks like on a page

In [I00009.md](/workspace/src/content/entity/I00009.md), the old page had:

- `Kind [Wilhelmina Johanna Voorbraak](../i00006/)`
- a matching chronology line for her birth

In the regenerated page, both lines are missing.

### Why one bug affects many files

This bug happens whenever a family has exactly one child and gedq emits `chil` as a single string instead of a JSON list. That is why 40 pages fall into this same cluster.

### Mental model

Think of it like this:

- correct: one box containing one child ID
- actual bug: the box gets shredded into separate letters and digits
- result: the program can no longer tell who the child is

## Appendix B: Name-Source Ordering and Grouping Drift

### Beginner explanation

People can have multiple names in GEDCOM, for example a birth name and a later variant.
Each name can also be linked to different sources.

The old parser kept those name occurrences in a very specific structure. Our new adapter reconstructs them from gedq using source `CITES` rows and groups them by:

- person ID
- name text value

That means we usually keep the right source set, but we do not always keep the exact old order or the exact old "which source belonged to which repeated NAME occurrence" grouping.

### What that looks like on a page

In [I00240.md](/workspace/src/content/entity/I00240.md), the old page had:

- `Naam: Wilhelmina van Dosselaar` with source links in one order

The new page still has the same name and the same source links, but the links appear in a different order.

In [I00021.md](/workspace/src/content/entity/I00021.md), the alternate names still exist, but some sources are grouped under the name variants in a different order than before.

### Why this is not the same as missing data

This class is usually not "we lost the source completely."
It is more often:

- same name
- same or very similar source set
- different order or grouping

So this is more of a reconstruction-fidelity problem than a total data-loss problem.

### Mental model

Imagine you had two folders:

- folder A for one spelling of a name
- folder B for another spelling

The new adapter keeps the papers, but may put some papers into the right folders in a slightly different order, or under the repeated name text instead of the original exact GEDCOM occurrence.

## Appendix C: Name-Attached Footnote Loss

### Beginner explanation

Some notes in the old output were attached specifically to a name, not just to the person in general.

The public gedq JSON is good enough to preserve many things, but it does not always preserve the old parser's exact "this note belonged to this specific `NAME` occurrence" detail.

So in a few cases, the person and the name are still there, but a footnote that used to appear under the name line no longer shows up.

### What that looks like on a page

In [I00014.md](/workspace/src/content/entity/I00014.md), the old page had:

- `Naam: Constantia Engels [^1] ...`
- a matching `### Voetnoten` block explaining that footnote

The new page still has the name and sources, but that specific name-attached footnote is gone.

### Why this is rare

Only one file currently falls into this bucket. That makes it a special edge case, not the main migration bug.

### Inspection result

We checked whether this footnote could be reconstructed from the currently allowed public gedq CLI surfaces.

Result: **not safely fixable with the current documented contract**.

Why:

- the raw GEDCOM clearly shows the note is attached under the first `NAME` for `I00014`
- the public gedq person JSON exposes the name values and their source-line positions
- but it does **not** expose the actual `NAME`-attached note text on that `NAME` structure
- documented expansions such as `person --expand NAME` and `person --expand all` still do not surface that note text

So a local fix would require either:

1. reading raw GEDCOM lines again during generation, which cuts against the migration boundary, or
2. a new documented gedq surface that exposes `NAME`-attached notes directly.

### Recommendation

No residual special handling is needed. Keep rendering name footnotes from `names[].notes` and treat any future loss of a `NAME`-attached note as a regression.

### Mental model

Think of the old system as having a sticky note attached to one exact name label.
The new system still has the label, but the sticky note attachment point is no longer visible in the public JSON.

## Appendix D: Record-Level Source Drop

### Beginner explanation

This is similar to Appendix A, but for source IDs instead of child IDs.

Some gedq records emit top-level `source_ids` as a single string, for example:

```json
"source_ids": "S00012"
```

Our adapter currently loops over `record.get("source_ids", [])` as if it were always a list.

If it is a string, Python iterates over the characters:

```python
'S', '0', '0', '0', '1', '2'
```

Those are not real source IDs, so the source lookup fails and the source disappears from the page.

### What that looks like on a page

In [I00006.md](/workspace/src/content/entity/I00006.md), the old page had this source in `Bronnen lijst`:

- `Bevolkingsregister Muiden 1900-1921 H-M page 129`

In the regenerated page, that line is missing.

The raw gedq payload for that person includes:

```json
"source_ids": "S00012"
```

So the source exists in the input, but our adapter is reading it incorrectly.

### Mental model

It is the same kind of mistake as Appendix A:

- expected: one complete source ID
- actual bug: split into separate letters and digits
- result: source cannot be looked up, so it disappears from `Bronnen lijst`
